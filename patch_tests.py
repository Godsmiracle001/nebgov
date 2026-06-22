import re

with open('contracts/liquidity/src/tests.rs', 'r') as f:
    content = f.read()

# Replace setup_liquidity signature and body
old_setup = """fn setup_liquidity() -> (Env, Address, Address, Address, Address) {
    let env = Env::default();
    env.mock_all_auths();

    let contract_id = env.register(LiquidityContract, ());
    let client = LiquidityContractClient::new(&env, &contract_id);

    let governor = Address::generate(&env);
    let provider = Address::generate(&env);
    let trader = Address::generate(&env);

    client.initialize(&governor);

    (env, contract_id, governor, provider, trader)
}"""

new_setup = """use soroban_sdk::token::StellarAssetClient;

fn setup_liquidity() -> (Env, Address, Address, Address, Address, Address, Address) {
    let env = Env::default();
    env.mock_all_auths();

    let contract_id = env.register(LiquidityContract, ());
    let client = LiquidityContractClient::new(&env, &contract_id);

    let governor = Address::generate(&env);
    let provider = Address::generate(&env);
    let trader = Address::generate(&env);
    let admin = Address::generate(&env);

    let token_a = env.register_stellar_asset_contract_v2(admin.clone()).address();
    let token_b = env.register_stellar_asset_contract_v2(admin.clone()).address();

    let sac_a = StellarAssetClient::new(&env, &token_a);
    let sac_b = StellarAssetClient::new(&env, &token_b);
    sac_a.mint(&provider, &1_000_000);
    sac_b.mint(&provider, &1_000_000);
    sac_a.mint(&trader, &1_000_000);
    sac_b.mint(&trader, &1_000_000);

    client.initialize(&governor);

    (env, contract_id, governor, provider, trader, token_a, token_b)
}"""
content = content.replace(old_setup, new_setup)

# Replace exactly 5 items in let bindings
content = re.sub(r'let \(([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^)]+)\)\s*=\s*setup_liquidity\(\);', r'let (\1, \2, \3, \4, \5, token_a, token_b) = setup_liquidity();', content)

# Replace client.add_liquidity calls with 5 arguments (ignoring the method name prefix)
content = re.sub(r'\.add_liquidity\(&([^,]+),\s*&([^,]+),\s*&([^,]+),\s*&([^,]+),\s*&([^)]+)\)', r'.add_liquidity(&\1, &\2, &\3, &token_a, &token_b, &\4, &\5)', content)

# Also fix `liquidity_client.add_liquidity` if there are any
# The above regex catches `.add_liquidity` so it works for `client` and `liquidity_client`.

with open('contracts/liquidity/src/tests.rs', 'w') as f:
    f.write(content)

