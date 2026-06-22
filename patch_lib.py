import re

with open('contracts/liquidity/src/lib.rs', 'r') as f:
    content = f.read()

# Add import
content = content.replace('use soroban_sdk::{contract, contractimpl, contracterror, contracttype, Address, Env};', 'use soroban_sdk::{contract, contractimpl, contracterror, contracttype, token::TokenClient, Address, Env};')

# Add DataKey
datakey_str = """enum DataKey {
    Governor,
    Pool(u32, u32),
    Position(Address, u32, u32),
}"""
new_datakey_str = """enum DataKey {
    Governor,
    Pool(u32, u32),
    Position(Address, u32, u32),
    PoolTokens(u32, u32),
}"""
content = content.replace(datakey_str, new_datakey_str)

# Update add_liquidity
add_liq_sig = """    pub fn add_liquidity(
        env: Env,
        provider: Address,
        outcome_a: u32,
        outcome_b: u32,
        amount_a: i128,
        amount_b: i128,
    ) -> i128 {"""
new_add_liq_sig = """    pub fn add_liquidity(
        env: Env,
        provider: Address,
        outcome_a: u32,
        outcome_b: u32,
        token_a: Address,
        token_b: Address,
        amount_a: i128,
        amount_b: i128,
    ) -> i128 {"""
content = content.replace(add_liq_sig, new_add_liq_sig)

# In add_liquidity, after provider.require_auth();
auth_str = """        provider.require_auth();

        if amount_a <= 0 || amount_b <= 0 {"""
new_auth_str = """        provider.require_auth();

        if amount_a <= 0 || amount_b <= 0 {"""
# wait, let's just insert before `let pool_key`
pool_key_str = """        let pool_key = Self::pool_key(outcome_a, outcome_b);"""
new_pool_key_str = """        let tokens_key = DataKey::PoolTokens(outcome_a, outcome_b);
        if let Some((stored_a, stored_b)) = env.storage().persistent().get::<(Address, Address)>(&tokens_key) {
            assert!(token_a == stored_a && token_b == stored_b, "token mismatch");
        } else {
            env.storage().persistent().set(&tokens_key, &(token_a.clone(), token_b.clone()));
        }

        TokenClient::new(&env, &token_a).transfer(&provider, &env.current_contract_address(), &amount_a);
        TokenClient::new(&env, &token_b).transfer(&provider, &env.current_contract_address(), &amount_b);

        let pool_key = Self::pool_key(outcome_a, outcome_b);"""
content = content.replace(pool_key_str, new_pool_key_str)

# In remove_liquidity
remove_liq_auth = """        provider.require_auth();

        // Security: validate caller inputs before any state mutation or token transfer."""
new_remove_liq_auth = """        provider.require_auth();

        // Security: validate caller inputs before any state mutation or token transfer."""
# Let's insert token transfer at the end of remove_liquidity, before return
remove_liq_end = """        env.storage().persistent().set(&pool_key, &pool);
        env.storage().persistent().set(&position_key, &position);

        (amount_a, amount_b)"""
new_remove_liq_end = """        env.storage().persistent().set(&pool_key, &pool);
        env.storage().persistent().set(&position_key, &position);

        let tokens_key = DataKey::PoolTokens(outcome_a, outcome_b);
        let (token_a, token_b): (Address, Address) = env.storage().persistent().get(&tokens_key).expect("pool tokens not found");
        
        TokenClient::new(&env, &token_a).transfer(&env.current_contract_address(), &provider, &amount_a);
        TokenClient::new(&env, &token_b).transfer(&env.current_contract_address(), &provider, &amount_b);

        (amount_a, amount_b)"""
content = content.replace(remove_liq_end, new_remove_liq_end)

# In swap
swap_end = """        pool.reserve_a += amount_in;
        pool.reserve_b -= amount_out_with_fee;
        env.storage().persistent().set(&pool_key, &pool);

        amount_out_with_fee"""
new_swap_end = """        pool.reserve_a += amount_in;
        pool.reserve_b -= amount_out_with_fee;
        env.storage().persistent().set(&pool_key, &pool);

        let tokens_key = DataKey::PoolTokens(outcome_in, outcome_out);
        let (token_in, token_out): (Address, Address) = env.storage().persistent().get(&tokens_key).expect("pool tokens not found");
        
        TokenClient::new(&env, &token_in).transfer(&trader, &env.current_contract_address(), &amount_in);
        TokenClient::new(&env, &token_out).transfer(&env.current_contract_address(), &trader, &amount_out_with_fee);

        amount_out_with_fee"""
content = content.replace(swap_end, new_swap_end)

with open('contracts/liquidity/src/lib.rs', 'w') as f:
    f.write(content)

