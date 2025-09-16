-- 可选：把名为 Demo Asset 的旧数据清掉，避免重复（不会动其他资产）
DO $$
DECLARE
  aid BIGINT;
BEGIN
  SELECT asset_id INTO aid FROM public.assets WHERE name = 'Demo Asset';
  IF aid IS NOT NULL THEN
    DELETE FROM public.transactions WHERE asset_id = aid;
    DELETE FROM public.fractions    WHERE asset_id = aid;
    DELETE FROM public.assets       WHERE asset_id = aid;
  END IF;
END $$ LANGUAGE plpgsql;

-- 插入两个用户（若已存在则跳过）——不使用 ON CONFLICT
INSERT INTO public.users(is_manager, email, password, username, create_time)
SELECT FALSE, 'a@example.com', md5('a'), 'user_a', NOW()
WHERE NOT EXISTS (SELECT 1 FROM public.users WHERE username = 'user_a');

INSERT INTO public.users(is_manager, email, password, username, create_time)
SELECT FALSE, 'b@example.com', md5('b'), 'user_b', NOW()
WHERE NOT EXISTS (SELECT 1 FROM public.users WHERE username = 'user_b');

-- 插入一个资产（若已存在则跳过）——不使用 ON CONFLICT
INSERT INTO public.assets
  (name, description, max_fractions, min_fractions, available_fractions,
   submitted_by_users_user_id, created_at, status, approved_at, approved_by_users_user_id)
SELECT 'Demo Asset', 'demo', 10, 1, 0, NULL, NOW(), 'approved', NOW(), NULL
WHERE NOT EXISTS (SELECT 1 FROM public.assets WHERE name = 'Demo Asset');

-- A 拥有 10 -> 卖给 B 4：fractions 两条、transactions 一条
DO $$
DECLARE
  uid_a BIGINT;
  uid_b BIGINT;
  aid   BIGINT;
  base_frac_id BIGINT;
  new_frac_id  BIGINT;
  qty   INT := 4;
  t0    TIMESTAMP := NOW();
BEGIN
  SELECT user_id INTO uid_a FROM public.users WHERE username = 'user_a';
  SELECT user_id INTO uid_b FROM public.users WHERE username = 'user_b';
  SELECT asset_id INTO aid   FROM public.assets WHERE name = 'Demo Asset';

  -- 先让 A 拥有整块 10
  INSERT INTO public.fractions(asset_id, slices, current_owner_user_id, owners_history,
                               parent_fraction_id, created_at, updated_at)
  VALUES (
    aid, 10, uid_a,
    jsonb_build_array(jsonb_build_object('user_id', uid_a, 'event','create','qty',10,'time',t0)),
    NULL, t0, t0
  )
  RETURNING fraction_id INTO base_frac_id;

  -- A 卖出 4：把原 fraction -4，并记录历史
  UPDATE public.fractions
  SET slices = slices - qty,
      owners_history = owners_history
        || jsonb_build_object('user_id', uid_a, 'event','transfer_out','qty', qty, 'time', t0 + interval '1 minute')
  WHERE fraction_id = base_frac_id;

  -- 给 B 新建一个 fraction(4)
  INSERT INTO public.fractions(asset_id, slices, current_owner_user_id, owners_history,
                               parent_fraction_id, created_at, updated_at)
  VALUES (
    aid, qty, uid_b,
    jsonb_build_array(
      jsonb_build_object('user_id', uid_a, 'event','split_from',  'qty', qty, 'time', t0 + interval '1 minute'),
      jsonb_build_object('user_id', uid_b, 'event','transfer_in', 'qty', qty, 'time', t0 + interval '1 minute')
    ),
    base_frac_id,
    t0 + interval '1 minute',
    t0 + interval '1 minute'
  )
  RETURNING fraction_id INTO new_frac_id;

  -- 写一条交易流水
  INSERT INTO public.transactions(
    asset_id, source_fraction_id, new_fraction_id, quantity,
    from_users_user_id, to_users_user_id, trade_time, unit_price, currency, notes
  )
  VALUES (
    aid, base_frac_id, new_frac_id, qty,
    uid_a, uid_b, t0 + interval '1 minute',
    NULL, 'USD', 'demo trade'
  );

  -- 回填可用量
  UPDATE public.assets a
  SET available_fractions = GREATEST(
    0,
    a.max_fractions - COALESCE((SELECT SUM(f.slices) FROM public.fractions f WHERE f.asset_id = a.asset_id), 0)::int
  )
  WHERE a.asset_id = aid;
END $$ LANGUAGE plpgsql;

-- 验证（应为：fractions 两行：A=6, B=4；transactions 一行：qty=4）
SELECT fraction_id, asset_id, slices, current_owner_user_id
FROM public.fractions
WHERE asset_id = (SELECT asset_id FROM public.assets WHERE name='Demo Asset')
ORDER BY fraction_id;

SELECT transaction_id, asset_id, source_fraction_id, new_fraction_id, quantity,
       from_users_user_id, to_users_user_id, trade_time
FROM public.transactions
WHERE asset_id = (SELECT asset_id FROM public.assets WHERE name='Demo Asset')
ORDER BY transaction_id;





//////-- 1) 如果 user_c 不存在就创建
INSERT INTO public.users(is_manager, email, password, username, create_time)
SELECT FALSE, 'c@example.com', md5('c'), 'user_c', NOW()
WHERE NOT EXISTS (SELECT 1 FROM public.users WHERE username = 'user_c');

-- 2) 执行两笔交易（C 从 38 买 1、再从 39 买 1）
DO $$
DECLARE
  v_frac_a  bigint := 38;  -- A 的 fraction
  v_frac_b  bigint := 39;  -- B 的 fraction

  uid_c     bigint;
  f38_asset bigint; f38_seller bigint;
  f39_asset bigint; f39_seller bigint; f39_hist jsonb;
  new_frac_from_38 bigint;
  new_frac_from_39 bigint;
  t1 timestamp := NOW();
  t2 timestamp := NOW() + interval '1 minute';
BEGIN
  SELECT user_id INTO uid_c FROM public.users WHERE username='user_c';
  IF uid_c IS NULL THEN
    RAISE EXCEPTION 'user_c creation failed or not found.';
  END IF;

  -- C 从 A（frac 38）买 1
  SELECT asset_id, current_owner_user_id INTO f38_asset, f38_seller
  FROM public.fractions WHERE fraction_id = v_frac_a FOR UPDATE;
  IF f38_asset IS NULL THEN RAISE EXCEPTION 'Fraction % not found', v_frac_a; END IF;

  UPDATE public.fractions
  SET slices = slices - 1,
      owners_history = owners_history
        || jsonb_build_object('user_id', f38_seller, 'event','transfer_out','qty',1,'time', t1)
  WHERE fraction_id = v_frac_a;

  INSERT INTO public.fractions(asset_id, slices, current_owner_user_id, owners_history, parent_fraction_id, created_at, updated_at)
  VALUES (
    f38_asset, 1, uid_c,
    jsonb_build_array(
      jsonb_build_object('user_id', f38_seller, 'event','split_from','qty',1,'time',t1),
      jsonb_build_object('user_id', uid_c,      'event','transfer_in','qty',1,'time',t1)
    ),
    v_frac_a, t1, t1
  )
  RETURNING fraction_id INTO new_frac_from_38;

  INSERT INTO public.transactions(asset_id, source_fraction_id, new_fraction_id, quantity,
                                  from_users_user_id, to_users_user_id, trade_time, currency, notes)
  VALUES (f38_asset, v_frac_a, new_frac_from_38, 1, f38_seller, uid_c, t1, 'USD', 'C buys 1 from A');

  -- C 从 B（frac 39）买 1（继承 39 的历史 ⇒ [A,B,C]）
  SELECT asset_id, current_owner_user_id, owners_history
  INTO f39_asset, f39_seller, f39_hist
  FROM public.fractions WHERE fraction_id = v_frac_b FOR UPDATE;
  IF f39_asset IS NULL THEN RAISE EXCEPTION 'Fraction % not found', v_frac_b; END IF;

  UPDATE public.fractions
  SET slices = slices - 1,
      owners_history = owners_history
        || jsonb_build_object('user_id', f39_seller, 'event','transfer_out','qty',1,'time', t2)
  WHERE fraction_id = v_frac_b;

  INSERT INTO public.fractions(asset_id, slices, current_owner_user_id, owners_history, parent_fraction_id, created_at, updated_at)
  VALUES (
    f39_asset, 1, uid_c,
    f39_hist || jsonb_build_object('user_id', uid_c, 'event','transfer_in','qty',1,'time', t2),
    v_frac_b, t2, t2
  )
  RETURNING fraction_id INTO new_frac_from_39;

  INSERT INTO public.transactions(asset_id, source_fraction_id, new_fraction_id, quantity,
                                  from_users_user_id, to_users_user_id, trade_time, currency, notes)
  VALUES (f39_asset, v_frac_b, new_frac_from_39, 1, f39_seller, uid_c, t2, 'USD', 'C buys 1 from B');

  -- 可选：回填资产剩余量
  UPDATE public.assets a
  SET available_fractions = GREATEST(
    0,
    a.max_fractions - COALESCE((SELECT SUM(f.slices) FROM public.fractions f WHERE f.asset_id = a.asset_id), 0)::int
  )
  WHERE a.asset_id IN (f38_asset, f39_asset);
END $$ LANGUAGE plpgsql;


