from langchain_core.language_models import LLM
from langchain_core.outputs import GenerationChunk
from pydantic import Field
from typing import Optional, List, Iterator
from langchain_core.callbacks import CallbackManagerForLLMRun
import requests

class MyDualEndpointLLM(LLM):
    secret_key: str = Field()
    non_stream_url: str = Field()
    stream_url: str = Field()

    @property
    def _llm_type(self) -> str:
        return "dual-endpoint-wrapper"

    @property
    def _is_streaming(self) -> bool:
        return True  # Important for LangChain to recognize this model supports streaming

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        temperature: Optional[str] = None,
        top_p: Optional[str] = None,
        responseMaxTokens: Optional[int] = 16000,
    ) -> str:
        payload = {
            "Prompt": prompt,
            "intelligizeAIAccountType": 2,
            "endpointSecretKey": self.secret_key,
            "Source": "Backend - Dev - PBD",
            "Category": "Idea Extractor - CvF",
            "AppKey": "PBD",
            "LLMMetadata": True,
            "responseMaxTokens": responseMaxTokens,
        }

        if temperature is not None:
            payload["Temperature"] = temperature
        if top_p is not None:
            payload["TopP"] = top_p
        if stop:
            payload["StopSequences"] = stop

        response = requests.post(self.non_stream_url, json=payload)
        response.raise_for_status()
        try:
            result = response.json()
            return result['content'][0]['text']
        except (KeyError, IndexError):
            raise ValueError("Unexpected response format: " + str(result))

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs
    ) -> Iterator[GenerationChunk]:
        payload = {
            "Prompt": prompt,
            "intelligizeAIAccountType": 2,
            "endpointSecretKey": self.secret_key,
            "Source": "Backend - Dev - PBD",
            "Category": "Idea Extractor - CvF",
            "AppKey": "PBD",
            "responseMaxTokens": kwargs.get("responseMaxTokens", 16000),
        }
    
        if "temperature" in kwargs:
            payload["Temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            payload["TopP"] = kwargs["top_p"]
        if stop:
            payload["StopSequences"] = stop
    
        with requests.post(self.stream_url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    text = line.decode("utf-8").strip()
                    if run_manager:
                        run_manager.on_llm_new_token(text)
                    yield GenerationChunk(text=text)
