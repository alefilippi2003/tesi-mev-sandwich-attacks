WITH trades_puliti AS (
    SELECT 
        block_number,
        block_time,
        tx_hash,
        evt_index,
        tx_from,
        token_bought_address,
        token_sold_address,
        amount_usd 
    FROM dex.trades
    WHERE block_time >= DATE('2026-04-01')
      AND block_time < DATE('2026-05-01') 
      AND blockchain = 'ethereum' 
),
bot_legs AS (
    SELECT 
        f.block_number,
        f.block_time,
        f.tx_from AS attacker_address,
        f.tx_hash AS front_run_hash,
        f.evt_index AS front_run_index,
        f.amount_usd AS front_run_usd,
        b.tx_hash AS back_run_hash,
        b.evt_index AS back_run_index,
        b.amount_usd AS back_run_usd
    FROM trades_puliti f
    JOIN trades_puliti b 
        ON f.block_number = b.block_number 
        AND f.tx_from = b.tx_from
        AND f.evt_index < b.evt_index 
    WHERE 
        f.token_bought_address = b.token_sold_address 
        AND f.token_sold_address = b.token_bought_address
),
sandwich_base AS (
    SELECT DISTINCT
        s.block_number,
        s.block_time,
        s.attacker_address,
        s.front_run_hash,
        s.back_run_hash,
        s.front_run_usd,
        s.back_run_usd
    FROM bot_legs s
    JOIN trades_puliti v 
        ON s.block_number = v.block_number
    WHERE 
        v.evt_index > s.front_run_index 
        AND v.evt_index < s.back_run_index
        AND v.tx_from != s.attacker_address
)
SELECT 
    sb.block_number,
    sb.block_time,
    sb.attacker_address,
    sb.front_run_hash,
    sb.back_run_hash,
    sb.front_run_usd,
    sb.back_run_usd,
    (sb.back_run_usd - sb.front_run_usd) AS gross_profit_usd,
    tf.gas_used AS front_gas_used,
    (tf.gas_price / 1e9) AS front_gas_price_gwei,
    (tf.priority_fee_per_gas / 1e9) AS front_bribe_gwei,
    tb.gas_used AS back_gas_used,
    (tb.gas_price / 1e9) AS back_gas_price_gwei,
    (tb.priority_fee_per_gas / 1e9) AS back_bribe_gwei
FROM sandwich_base sb
JOIN ethereum.transactions tf 
    ON sb.front_run_hash = tf.hash 
    AND sb.block_number = tf.block_number 
JOIN ethereum.transactions tb 
    ON sb.back_run_hash = tb.hash 
    AND sb.block_number = tb.block_number 