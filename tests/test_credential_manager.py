"""Testes para serviço de gerenciamento de credenciais Deriv."""
import pytest
from deriv_organismo.services.credential_manager import CredentialManager


def test_credential_manager_encrypts_token():
    """CredentialManager criptografa token antes de armazenar."""
    manager = CredentialManager(secret_key="test-secret-key-32-bytes-long!!")
    
    encrypted = manager.encrypt_token("raw_token_abc123")
    
    assert encrypted != "raw_token_abc123"
    assert len(encrypted) > 0


def test_credential_manager_decrypts_token():
    """CredentialManager decriptografa token corretamente."""
    manager = CredentialManager(secret_key="test-secret-key-32-bytes-long!!")
    
    encrypted = manager.encrypt_token("raw_token_abc123")
    decrypted = manager.decrypt_token(encrypted)
    
    assert decrypted == "raw_token_abc123"


def test_credential_manager_different_keys_produce_different_ciphertexts():
    """Tokens criptografados com chaves diferentes produzem ciphertexts diferentes."""
    manager_a = CredentialManager(secret_key="key-a-32-bytes-long-enough!!!!!")
    manager_b = CredentialManager(secret_key="key-b-32-bytes-long-enough!!!!!")
    
    encrypted_a = manager_a.encrypt_token("same_token")
    encrypted_b = manager_b.encrypt_token("same_token")
    
    assert encrypted_a != encrypted_b


def test_credential_manager_rejects_empty_token():
    """CredentialManager rejeita token vazio."""
    manager = CredentialManager(secret_key="test-secret-key-32-bytes-long!!")
    
    with pytest.raises(ValueError, match="token cannot be empty"):
        manager.encrypt_token("")


def test_credential_manager_rejects_invalid_decryption():
    """CredentialManager falha ao decriptografar ciphertext inválido."""
    manager = CredentialManager(secret_key="test-secret-key-32-bytes-long!!")
    
    with pytest.raises(ValueError, match="invalid ciphertext"):
        manager.decrypt_token("not-a-valid-ciphertext")
