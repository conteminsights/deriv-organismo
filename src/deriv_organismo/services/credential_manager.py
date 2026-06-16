"""Serviço de gerenciamento de credenciais Deriv com criptografia."""
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken


class CredentialManager:
    """Gerencia criptografia e descriptografia de tokens Deriv."""
    
    def __init__(self, secret_key: str):
        """
        Inicializa o CredentialManager com uma chave secreta.
        
        Args:
            secret_key: Chave secreta para derivação da chave Fernet.
                       Deve ter pelo menos 32 bytes para segurança adequada.
        """
        if not secret_key:
            raise ValueError("secret_key cannot be empty")
        
        # Deriva uma chave Fernet de 32 bytes a partir da secret_key
        key_bytes = hashlib.sha256(secret_key.encode('utf-8')).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt_token(self, token: str) -> str:
        """
        Criptografa um token usando Fernet.
        
        Args:
            token: Token em texto plano a ser criptografado.
            
        Returns:
            String base64 com o token criptografado.
            
        Raises:
            ValueError: Se o token estiver vazio.
        """
        if not token:
            raise ValueError("token cannot be empty")
        
        return self._fernet.encrypt(token.encode('utf-8')).decode('utf-8')
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Descriptografa um token previamente criptografado.
        
        Args:
            encrypted_token: Token criptografado em base64.
            
        Returns:
            Token original em texto plano.
            
        Raises:
            ValueError: Se o ciphertext for inválido ou a descriptografia falhar.
        """
        if not encrypted_token:
            raise ValueError("encrypted_token cannot be empty")
        
        try:
            decrypted_bytes = self._fernet.decrypt(encrypted_token.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            raise ValueError("invalid ciphertext")
