import os
from functools import partial

import click
import numpy as np
import random

from concrete import fhe
from concrete.fhe import tfhers
from concrete.fhe.values import ClearScalar

# ########## Params #####################
LWE_DIM = 909
GLWE_DIM = 1
POLY_SIZE = 4096
PBS_BASE_LOG = 15
PBS_LEVEL = 2
MSG_WIDTH = 2
CARRY_WIDTH = 3
ENCRYPTION_KEY_CHOICE = tfhers.EncryptionKeyChoice.BIG
# LWE_NOISE_DISTR = 0
LWE_NOISE_DISTR = 1.0994794733558207e-6
GLWE_NOISE_DISTR = 2.168404344971009e-19
# #######################################

# ########## Params #####################
# ### PARAM_MESSAGE_2_CARRY_2_KS_PBS_TUNIFORM_2M64
# LWE_DIM = 887
# GLWE_DIM = 1
# POLY_SIZE = 2048
# PBS_BASE_LOG = 22
# PBS_LEVEL = 1
# MSG_WIDTH = 2
# CARRY_WIDTH = 2
# ENCRYPTION_KEY_CHOICE = tfhers.EncryptionKeyChoice.BIG
# # LWE_NOISE_DISTR = 0
# # noise params are not properly set i think. 
# # PARAM_MESSAGE_2_CARRY_2_KS_PBS_TUNIFORM_2M64 has t_uniform noise distribution, 
# # but it seems the below numbers are for gaussian distribution. 
# LWE_NOISE_DISTR = 1.0994794733558207e-6
# GLWE_NOISE_DISTR = 2.168404344971009e-19
# #######################################

assert GLWE_DIM == 1, "glwe dim must be 1"

### Options ###########################
FHEUINT_PRECISION = 8
#######################################


tfhers_params = tfhers.CryptoParams(
    lwe_dimension=LWE_DIM,
    glwe_dimension=GLWE_DIM,
    polynomial_size=POLY_SIZE,
    pbs_base_log=PBS_BASE_LOG,
    pbs_level=PBS_LEVEL,
    lwe_noise_distribution=LWE_NOISE_DISTR,
    glwe_noise_distribution=GLWE_NOISE_DISTR,
    encryption_key_choice=ENCRYPTION_KEY_CHOICE,
)
tfhers_type = tfhers.TFHERSIntegerType(
    is_signed=False,
    bit_width=FHEUINT_PRECISION,
    carry_width=CARRY_WIDTH,
    msg_width=MSG_WIDTH,
    params=tfhers_params,
)

# this partial will help us create TFHERSInteger with the given type instead of calling
# tfhers.TFHERSInteger(tfhers_type, value) every time
tfhers_int = partial(tfhers.TFHERSInteger, tfhers_type)


# def compute(tfhers_x, tfhers_y, aa_0, aa_1, aa_2):
# def compute(tfhers_x, tfhers_y, aa_0):
def compute(tfhers_x, tfhers_y):
    ####### TFHE-rs to Concrete #########

    # x and y are supposed to be TFHE-rs values.
    # to_native will use type information from x and y to do
    # a correct conversion from TFHE-rs to Concrete
    concrete_x = tfhers.to_native(tfhers_x)
    concrete_y = tfhers.to_native(tfhers_y)
    # a_0 = tfhers.to_native(aa_0)
    # a_1 = tfhers.to_native(aa_1)
    # a_2 = tfhers.to_native(aa_2)
    ####### TFHE-rs to Concrete #########

    ####### Concrete Computation ########
    # concrete_res = (concrete_x + concrete_y) % 213
    # concrete_res = (a_0 * concrete_x * concrete_x + a_1 * concrete_y * concrete_y + a_2 *concrete_x * concrete_y) % 213
    # concrete_res = (aa_0 * concrete_x * concrete_x + aa_1 * concrete_y * concrete_y + aa_2 *concrete_x * concrete_y) % 213
    # concrete_res = (aa_0 *concrete_x * concrete_y) % 213
    # concrete_res = (a_0 *concrete_x * concrete_y) % 213
    concrete_res = (concrete_x * concrete_y) % 213
    ####### Concrete Computation ########

    ####### Concrete to TFHE-rs #########
    tfhers_res = tfhers.from_native(
        concrete_res, tfhers_type
    )  # we have to specify the type we want to convert to
    ####### Concrete to TFHE-rs #########
    return tfhers_res


def ccompilee():
    # compiler = fhe.Compiler(compute, {"tfhers_x": "encrypted", "tfhers_y": "encrypted", "aa_0" : "clear", "aa_1": "clear", "aa_2": "clear"})
    # compiler = fhe.Compiler(compute, {"tfhers_x": "encrypted", "tfhers_y": "encrypted", "aa_0" : "clear"})
    compiler = fhe.Compiler(compute, {"tfhers_x": "encrypted", "tfhers_y": "encrypted"})

    val = 10
    # print("tfhers_int(120): {}", tfhers_int(120))
    # inputset = [(tfhers_int(120), tfhers_int(120))]
    # inputset = [(tfhers_int(val), tfhers_int(val))]
    # inputset = [(tfhers_int(val), tfhers_int(val), tfhers_int(val))]
    # inputset = [(tfhers_int(random.randint(1, val)), tfhers_int(random.randint(1, val)), random.randint(1, val)) for _ in range(10)]
    # inputset = [(tfhers_int(random.randint(1, val)), tfhers_int(random.randint(1, val)), tfhers_int(random.randint(1, val))) for _ in range(10)]
    # inputset = [(tfhers_int(random.randint(1, val)), tfhers_int(random.randint(1, val))) for _ in range(10)]
    # inputset = [(tfhers_int(val), tfhers_int(val), tfhers_int(val), tfhers_int(val), tfhers_int(val))]

    inputset_int = [(5, 6), (8, 7), (9, 10), (12, 5), (7, 13), (14, 15), (10, 11), (15, 12), (12, 12)]
    inputset = [((tfhers_int(a), tfhers_int(b))) for a, b in inputset_int]
    print("ccompilee: check1")
    circuit = compiler.compile(inputset)
    print("ccompilee: check2")

    # print("Testing compiler...")
    # encrypted_x, encrypted_y, encrypted_a0 = circuit.encrypt(tfhers_type.encode(2), tfhers_type.encode(3), tfhers_type.encode(4))
    # print("encrypted_x: {}".format(encrypted_x))
    # print("encrypted_y: {}".format(encrypted_y))
    # print("encrypted_a0: {}".format(encrypted_a0))
    # # run
    # encrypted_result = circuit.run(encrypted_x, encrypted_y, encrypted_a0)
    # # decrypt
    # result = circuit.decrypt(encrypted_result)
    # # decode
    # decoded = tfhers_type.decode(result)
    # print("Testing compiler... DONE, decoded value: {}".format(decoded))

    tfhers_bridge = tfhers.new_bridge(circuit=circuit)
    print("ccompilee: check3")
    return circuit, tfhers_bridge


@click.group()
def cli():
    pass


@cli.command()
@click.option("-s", "--secret-key", type=str, required=False)
@click.option("-o", "--output-secret-key", type=str, required=True)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
def keygen(output_secret_key: str, secret_key: str, concrete_keyset_path: str):
    """Concrete Key Generation"""

    print("ccompilee: starting")
    circuit, tfhers_bridge = ccompilee()
    print("ccompilee: done")

    if os.path.exists(concrete_keyset_path):
        print(f"removing old keyset at '{concrete_keyset_path}'")
        os.remove(concrete_keyset_path)

    if secret_key:
        print(f"partial keygen from sk at '{secret_key}'")
        # load the initial secret key to use for keygen
        with open(
            secret_key,
            "rb",
        ) as f:
            buff = f.read()
        input_idx_to_key = {0: buff, 1: buff}
        tfhers_bridge.keygen_with_initial_keys(input_idx_to_key_buffer=input_idx_to_key)
    else:
        print("full keygen")
        circuit.keygen()

    print(f"saving Concrete keyset")
    circuit.client.keys.save(concrete_keyset_path)
    print(f"saved Concrete keyset to '{concrete_keyset_path}'")

    sk: bytes = tfhers_bridge.serialize_input_secret_key(input_idx=0)
    print(f"writing secret key of size {len(sk)} to '{output_secret_key}'")
    with open(output_secret_key, "wb") as f:
        f.write(sk)


@cli.command()
@click.option("-c1", "--rust-ct-1", type=str, required=True)
@click.option("-c2", "--rust-ct-2", type=str, required=True)
@click.option("-o", "--output-rust-ct", type=str, required=False)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
@click.option("-a0", "--a-0", type=int, required=True)
# @click.option("-a1", "--a-1", type=int, required=True)
# @click.option("-a2", "--a-2", type=int, required=True)
# def run(rust_ct_1: str, rust_ct_2: str, output_rust_ct: str, concrete_keyset_path: str, a_0: int, a_1: int, a_2: int):
def run(rust_ct_1: str, rust_ct_2: str, output_rust_ct: str, concrete_keyset_path: str, a_0: int):
    """Run circuit"""
    circuit, tfhers_bridge = ccompilee()

    if not os.path.exists(concrete_keyset_path):
        raise RuntimeError("cannot find keys, you should run keygen before")
    print(f"loading keys from '{concrete_keyset_path}'")
    circuit.client.keys.load(concrete_keyset_path)

    # read tfhers int from file
    with open(rust_ct_1, "rb") as f:
        buff = f.read()
    # import fheuint8 and get its description
    tfhers_uint8_x = tfhers_bridge.import_value(buff, input_idx=0)

    # read tfhers int from file
    with open(rust_ct_2, "rb") as f:
        buff = f.read()
    # import fheuint8 and get its description
    tfhers_uint8_y = tfhers_bridge.import_value(buff, input_idx=1)

    encrypted_x, encrypted_y = tfhers_uint8_x, tfhers_uint8_y

    print("Testing well-formedness of ciphertexts...")
    plain_x = tfhers_type.decode(circuit.decrypt(encrypted_x))
    plain_y = tfhers_type.decode(circuit.decrypt(encrypted_y))
    print("Testing well-formedness of ciphertexts... DONE, x: {}, y: {}".format(plain_x, plain_y))

    print(f"Homomorphic evaluation...")
    # encrypted_result = circuit.run(encrypted_x, encrypted_y, a_0, a_1, a_2)
    # encrypted_result = circuit.run(encrypted_x, encrypted_y, a_0)
    # encrypted_result = circuit.run(encrypted_x, encrypted_y, ClearScalar(a_0))
    # _, _, encrypted_a0 = circuit.encrypt(None, None, a_0)
    _, _, encrypted_a0 = circuit.encrypt(None, None, tfhers_type.encode(a_0))
    print("encrypted_a0: {}".format(encrypted_a0))
    # encrypted_a0 = tfhers_type.encode(a_0)
    print("Running FHE circuit...")
    encrypted_result = circuit.run(encrypted_x, encrypted_y, encrypted_a0)
    print("Running FHE circuit... DONE")
    if output_rust_ct:
        print("exporting Rust ciphertexts")
        # export fheuint8
        # it seems that buff is ill-formed. It's length should be a multiple of 16 but it is not.
        # In my run, it is short by 8 bytes.
        buff = tfhers_bridge.export_value(encrypted_result, output_idx=0)
        # appending zero bytes at the end of buff to make its length a multiple of 16.
        padding_length = (16 - (len(buff) % 16)) % 16
        print("buff len: {}".format(len(buff)))
        buff = buff + b'\x00' * padding_length
        print("buff len: {}".format(len(buff)))
        # write it to file
        with open(output_rust_ct, "wb") as f:
            f.write(buff)
    else:
        print("Decrypting the result...")
        result = circuit.decrypt(encrypted_result)
        decoded = tfhers_type.decode(result)
        print(f"Concrete decryption result: raw({result}), decoded({decoded})")

def export_helper(tfhers_bridge, encrypted_result, output_idx, file_path):
    # export fheuint8
    # it seems that buff is ill-formed. It's length should be a multiple of 16 but it is not.
    # In my run, it is short by 8 bytes.
    buff = tfhers_bridge.export_value(encrypted_result, output_idx=output_idx)
    # appending zero bytes at the end of buff to make its length a multiple of 16.
    padding_length = (16 - (len(buff) % 16)) % 16
    print("buff len: {}".format(len(buff)))
    buff = buff + b'\x00' * padding_length
    print("buff len: {}".format(len(buff)))
    # write it to file
    with open(file_path, "wb") as f:
        f.write(buff)

@cli.command()
@click.option("-c1", "--rust-ct-1", type=str, required=True)
@click.option("-c2", "--rust-ct-2", type=str, required=True)
@click.option("-o", "--output-rust-ct", type=str, required=False)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
@click.option("-x", "--x-input", type=int, required=True)
@click.option("-y", "--y-input", type=int, required=True)
# @click.option("-a0", "--a-0", type=int, required=True)
# @click.option("-a1", "--a-1", type=int, required=True)
# @click.option("-a2", "--a-2", type=int, required=True)
# def runfull(rust_ct_1: str, rust_ct_2: str, output_rust_ct: str, concrete_keyset_path: str, x_input: int, y_input: int, a_0: int):
def runfull(rust_ct_1: str, rust_ct_2: str, output_rust_ct: str, concrete_keyset_path: str, x_input: int, y_input: int):
    """Run circuit"""
    circuit, tfhers_bridge = ccompilee()

    if not os.path.exists(concrete_keyset_path):
        raise RuntimeError("cannot find keys, you should run keygen before")
    print(f"loading keys from '{concrete_keyset_path}'")
    circuit.client.keys.load(concrete_keyset_path)

    print("Testing compiler...")
    # encrypted_x, encrypted_y, encrypted_a0 = circuit.encrypt(tfhers_type.encode(x_input), tfhers_type.encode(y_input), tfhers_type.encode(a_0))
    encrypted_x, encrypted_y = circuit.encrypt(tfhers_type.encode(x_input), tfhers_type.encode(y_input))
    print("encrypted_x: {}".format(encrypted_x))
    print("encrypted_y: {}".format(encrypted_y))
    # print("encrypted_a0: {}".format(encrypted_a0))
    print("exporting Rust encrypted_x")
    export_helper(tfhers_bridge, encrypted_x, 0, rust_ct_1)
    print("exporting Rust encrypted_y")
    export_helper(tfhers_bridge, encrypted_y, 0, rust_ct_2)
    
    print("Performing homomorphic evaluation")
    # run
    # encrypted_result = circuit.run(encrypted_x, encrypted_y, encrypted_a0)
    encrypted_result = circuit.run(encrypted_x, encrypted_y)

    if output_rust_ct:
        print("exporting Rust ciphertexts")
        # export fheuint8
        # it seems that buff is ill-formed. It's length should be a multiple of 16 but it is not.
        # In my run, it is short by 8 bytes.
        export_helper(tfhers_bridge, encrypted_result, 0, output_rust_ct)
        # buff = tfhers_bridge.export_value(encrypted_result, output_idx=0)
        # # appending zero bytes at the end of buff to make its length a multiple of 16.
        # padding_length = (16 - (len(buff) % 16)) % 16
        # print("buff len: {}".format(len(buff)))
        # buff = buff + b'\x00' * padding_length
        # print("buff len: {}".format(len(buff)))
        # # write it to file
        # with open(output_rust_ct, "wb") as f:
        #     f.write(buff)
    else:
        print("Decrypting the result...")
        result = circuit.decrypt(encrypted_result)
        decoded = tfhers_type.decode(result)
        print(f"Concrete decryption result: raw({result}), decoded({decoded})")


@cli.command()
@click.option("-c", "--rust-ct", type=str, required=True)
@click.option("-k", "--concrete-keyset-path", type=str, required=True)
def decrypt(rust_ct: str, concrete_keyset_path: str):
    """Run circuit"""
    circuit, tfhers_bridge = ccompilee()

    if not os.path.exists(concrete_keyset_path):
        raise RuntimeError("cannot find keys, you should run keygen before")
    print(f"loading keys from '{concrete_keyset_path}'")
    circuit.client.keys.load(concrete_keyset_path)

    # read tfhers int from file
    with open(rust_ct, "rb") as f:
        buff = f.read()
    # import fheuint8 and get its description
    encrypted_val = tfhers_bridge.import_value(buff, input_idx=0)

    print("Decrypting the ciphertext...")
    result = circuit.decrypt(encrypted_val)
    decoded = tfhers_type.decode(result)
    print(f"Concrete decryption result: raw({result}), decoded({decoded})")



if __name__ == "__main__":
    cli()
