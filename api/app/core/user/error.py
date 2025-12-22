class UnmatchedPasswordError(Exception):
    """Erro levantado quando as senhas não coincidem durante o registro do usuário."""
    pass


class EmailAlreadyExistsError(Exception):
    """Erro levantado quando o email já está registrado no sistema."""
    pass


class PasswordTooShortError(Exception):
    """Erro levantado quando a senha é muito curta."""
    pass
