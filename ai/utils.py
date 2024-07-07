from openai.types.chat import ChatCompletion

# from src.settings import settings


class BaseUtils:
    @staticmethod
    def token_price(response: ChatCompletion) -> float:
        prompt_token_price = settings.PROMPT_TOKEN_PRICE/1000000
        completion_token_price = settings.COMPLETION_TOKEN_PRICE/1000000
        token_price = (
                response.usage.prompt_tokens * prompt_token_price
                + response.usage.completion_tokens * completion_token_price)
        rounded_token_price = round(token_price, 3)
        return rounded_token_price
