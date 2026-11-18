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


class IAIndisponivelError(AppError):
    """A IA falhou (rede, 5xx, resposta inválida). O fluxo manual segue livre."""
    status_code = 503


class IATimeoutError(AppError):
    """A IA estourou o tempo limite de AI_TIMEOUT_SECONDS."""
    status_code = 504
