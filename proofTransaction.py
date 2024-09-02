import json
from web3 import Web3

# 이더리움 테스트 네트워크에 연결
web3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/90179eaf26074e30b3b7a5be6cebd39d'))

# 연결 확인
assert web3.is_connected(), "이더리움 네트워크에 연결 실패"

# Verifier.sol 스마트 계약 ABI
contract_abi = [
   {
      "inputs": [
         {
            "internalType": "bytes",
            "name": "proof",
            "type": "bytes"
         },
         {
            "internalType": "uint256[]",
            "name": "instances",
            "type": "uint256[]"
         }
      ],
      "name": "verifyProof",
      "outputs": [
         {
            "internalType": "bool",
            "name": "",
            "type": "bool"
         }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
   }
]

# 스마트 계약 주소 (Remix를 통해 배포된 주소)
contract_address = '0xefb53bf04fdb1f667c6fea47670ed7d84a9632ea'
checksum_address = web3.to_checksum_address(contract_address)

# 스마트 계약 인스턴스 생성
contract = web3.eth.contract(address=checksum_address, abi=contract_abi)

# 개인 키 파일에서 읽기
with open('key.json', 'r') as key_file:
    key_data = json.load(key_file)
    private_key = key_data['private_key']
    
# 개인 키로부터 공개 주소를 추출
account = web3.eth.account.from_key(private_key)
web3.eth.default_account = account.address

# proof.json 파일에서 proof와 instances 읽기
with open('./proof1/proof.json', 'r') as proof_file:
    proof_data = json.load(proof_file)
    proof = bytes.fromhex(proof_data['hex_proof'][2:])  # '0x'를 제거한 후 바이트 배열로 변환
    # 이중 배열을 일차원 배열로 변환
    instances = [int(instance, 16) for sublist in proof_data["pretty_public_inputs"]['outputs'] for instance in sublist]
    

# 스마트 계약의 verifyProof 함수 호출
tx = contract.functions.verifyProof(proof, instances).build_transaction({
    'from': web3.eth.default_account,
    'nonce': web3.eth.get_transaction_count(web3.eth.default_account),
    'gas': 2000000,
    'gasPrice': web3.to_wei('20', 'gwei')
})

# 트랜잭션 서명
signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)

# 트랜잭션 전송
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

# 트랜잭션 영수증 확인
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print("트랜잭션 영수증:", tx_receipt)

# 트랜잭션 성공 여부 확인
if tx_receipt.status == 1:
    print("검증 성공")
else:
    print("검증 실패 input을 다시 확인해 주세요")
# verifyProof 함수 결과 호출 및 출력
result = contract.functions.verifyProof(proof, instances).call({'from': web3.eth.default_account})
print("verifyProof 결과:", result)
