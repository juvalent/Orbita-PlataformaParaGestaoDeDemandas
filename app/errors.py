class AppError(Exception):
    """Erro de negócio. Vira uma resposta JSON com o status_code indicado."""
    status_code = 400

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ConflitoError(AppError):
    status_code = 409


class NaoAutenticadoError(AppError):
    status_code = 401


class ProibidoError(AppError):
    status_code = 403


class NaoEncontradoError(AppError):
    status_code = 404
