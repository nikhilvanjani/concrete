import os
import json
import math
from functools import partial

import click
import numpy as np

from concrete import fhe
from concrete.fhe import tfhers

from numpy.random import randint

# FIXME: should we move this to Concrete library directly, hidden to the user
def get_tfhers_params_and_type_and_int(crypto_params_json, precision):

    def int_log2(x):
        return int(math.log2(x))

    # Read crypto parameters from TFHE-rs in the json file
    with open(crypto_params_json) as f:
        tfhe_rs_crypto_param_dic = json.load(f)

    # pretty_json = json.dumps(tfhe_rs_crypto_param_dic, indent=4)
    # print(pretty_json)

    def int_log2(x):
        return int(math.log2(x))

    # FIXME Params: users shouldn't change them, should we hide it
    pbs_tfhe_rs_crypto_param_dic = tfhe_rs_crypto_param_dic["inner"]["block_parameters"]["PBS"]
    lwe_dim = pbs_tfhe_rs_crypto_param_dic["lwe_dimension"]
    glwe_dim = pbs_tfhe_rs_crypto_param_dic["glwe_dimension"]
    poly_size = pbs_tfhe_rs_crypto_param_dic["polynomial_size"]
    pbs_base_log = pbs_tfhe_rs_crypto_param_dic["pbs_base_log"]
    pbs_level = pbs_tfhe_rs_crypto_param_dic["pbs_level"]
    msg_width = int_log2(pbs_tfhe_rs_crypto_param_dic["message_modulus"])
    carry_width = int_log2(pbs_tfhe_rs_crypto_param_dic["carry_modulus"])
    encryption_key_choice = tfhers.EncryptionKeyChoice.BIG
    lwe_noise_distr = pbs_tfhe_rs_crypto_param_dic["lwe_noise_distribution"]["Gaussian"]["std"]
    glwe_noise_distr = pbs_tfhe_rs_crypto_param_dic["glwe_noise_distribution"]["Gaussian"]["std"]

    assert glwe_dim == 1, "glwe dim must be 1"

    tfhers_params = tfhers.CryptoParams(
        lwe_dimension=lwe_dim,
        glwe_dimension=glwe_dim,
        polynomial_size=poly_size,
        pbs_base_log=pbs_base_log,
        pbs_level=pbs_level,
        lwe_noise_distribution=lwe_noise_distr,
        glwe_noise_distribution=glwe_noise_distr,
        encryption_key_choice=encryption_key_choice,
    )
    tfhers_type = tfhers.TFHERSIntegerType(
        is_signed=False,
        bit_width=precision,
        carry_width=carry_width,
        msg_width=msg_width,
        params=tfhers_params,
    )
    tfhers_int = partial(tfhers.TFHERSInteger, tfhers_type)

    return tfhers_params, tfhers_type, tfhers_int

# Options: the user can change the following
# FIXME: explain FHEUINT_PRECISION, ie can it be changed
FHEUINT_PRECISION = 8
tfhers_params, tfhers_type, tfhers_int = get_tfhers_params_and_type_and_int('server_dir/crypto_params.json', FHEUINT_PRECISION)

# Describe the function you want to apply, on Concrete ciphertexts
def server_side_function_in_concrete(concrete_vars):
    t = (concrete_vars[0] + concrete_vars[1]) % 47
    t = t + ((2 * concrete_vars[2]) % 47)
    t = (t + 47 - (concrete_vars[3] % 47)) % 47
    return t

# The user must specify the range of the TFHE-rs inputs
# FIXME: why can't we set the limit at 256? It's needed for FHEUint8
# FIXME(vectorisation): make that we can use a tensor here
inputset_of_tfhe_rs_inputs = [(tfhers_int(randint(128)),
                               tfhers_int(randint(128)),
                               tfhers_int(randint(128)),
                               tfhers_int(randint(128))) for _ in range(100)]

# End of options

# This is the compiled function: user doesn't have to change this, except to
# add more inputs (ie, tfhers_z etc)
# FIXME(vectorisation): make that we can use a tensor here
def function_to_run_in_concrete(tfhers_vars_0, tfhers_vars_1, tfhers_vars_2, tfhers_vars_3):

    # Here, tfhers_x and tfhers_y are in TFHE-rs format

    # FIXME(vectorisation): make that we can use a tensor here
    tfhers_vars = (tfhers_vars_0, tfhers_vars_1, tfhers_vars_2, tfhers_vars_3)

    concrete_vars = []

    for v in tfhers_vars:
        concrete_vars.append(tfhers.to_native(v))

    # Here, concrete_vars are in Concrete format

    # Here we can apply whatever function we want in Concrete
    concrete_res = server_side_function_in_concrete(concrete_vars)

    # Here, concrete_res is in Concrete format

    tfhers_res = tfhers.from_native(
        concrete_res, tfhers_type
    )  # we have to specify the type we want to convert to


    # Here, tfhers_res is in TFHE-rs format

    return tfhers_res

# This is where we compile the function with Concrete: user doesn't have to
# change this, except to add more inputs (ie, tfhers_z etc)
def compile_concrete_function():
    dic_compilation = {}

    # FIXME(vectorisation): make that we can use a tensor here
    for i in range(4):
        dic_compilation[f"tfhers_vars_{i}"] = "encrypted"

    compiler = fhe.Compiler(function_to_run_in_concrete, dic_compilation)

    circuit = compiler.compile(inputset_of_tfhe_rs_inputs)

    tfhers_bridge = tfhers.new_bridge(circuit=circuit)
    return circuit, tfhers_bridge


@click.group()
def cli():
    pass

def read_var_from_file(tfhers_bridge, filename, input_idx):
    with open(filename, "rb") as f:
        buff = f.read()
    return tfhers_bridge.import_value(buff, input_idx=input_idx)


@cli.command()
@click.option("-s", "--secret-key", type=str, required=True)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
# This is where we generate the evaluation key at the Concrete format, from the
# secret key coming from TFHE-rs, on the client side
def keygen(secret_key: str, concrete_keyset_path: str):
    """Concrete Key Generation"""

    # Compile the Concrete function
    circuit, tfhers_bridge = compile_concrete_function()

    if os.path.exists(concrete_keyset_path):
        os.remove(concrete_keyset_path)

    # Load the initial secret key to use for keygen
    with open(
        secret_key,
        "rb",
    ) as f:
        buff = f.read()

    input_idx_to_key = {0: buff, 1: buff}
    tfhers_bridge.keygen_with_initial_keys(input_idx_to_key_buffer=input_idx_to_key)

    # FIXME: remove the secret key before saving. The secret key can be used for
    # debugging but should really be removed in production
    circuit.client.keys.save(concrete_keyset_path)


@cli.command()
@click.option("-c", "--rust-ct", type=str, required=True)
@click.option("-o", "--output-rust-ct", type=str, required=True)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
# This is the actual FHE computation, on the server side
def run(rust_ct: str, output_rust_ct: str, concrete_keyset_path: str):
    """Run circuit"""
    circuit, tfhers_bridge = compile_concrete_function()

    if not os.path.exists(concrete_keyset_path):
        raise RuntimeError("cannot find keys, you should run keygen before")

    circuit.client.keys.load(concrete_keyset_path)

    tfhers_vars = []

    for i, rust_ct_i in enumerate(rust_ct.split()):
        tfhers_vars.append(read_var_from_file(tfhers_bridge, rust_ct_i, input_idx=i))

    tfhers_vars = tuple(tfhers_vars)

    encrypted_result = circuit.run(tfhers_vars)

    # Export the result
    buff = tfhers_bridge.export_value(encrypted_result, output_idx=0)
    with open(output_rust_ct, "wb") as f:
        f.write(buff)

    # BCM BEGIN: to debug computations
    # FIXME: how does it decrypt? we are on the server side, we shouldn't have
    # the secret key. I think it's because the secret key is saved in concrete_keyset_path

    # x = circuit.decrypt(tfhers_uint8_x)
    # decoded = tfhers_type.decode(x)
    # print(f"Concrete decryption result: raw({x}), decoded({decoded})")

    # y = circuit.decrypt(tfhers_uint8_y)
    # decoded = tfhers_type.decode(y)
    # print(f"Concrete decryption result: raw({y}), decoded({decoded})")

    # result = circuit.decrypt(encrypted_result)
    # decoded = tfhers_type.decode(result)
    # print(f"Concrete decryption result: raw({result}), decoded({decoded})")
    # BCM END


if __name__ == "__main__":
    cli()
