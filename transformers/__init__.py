class AutoModelForCausalLM:
    @staticmethod
    def from_pretrained(model_id, torch_dtype=None, device_map=None):
        class Model:
            def __init__(self):
                self.model_id = model_id
            def eval(self):
                pass
            def generate(self, **kwargs):
                return [[0]]
        return Model()

class AutoTokenizer:
    @staticmethod
    def from_pretrained(model_id):
        class Tok:
            eos_token_id = 0
            def __call__(self, prompt, return_tensors=None):
                class Encoded(dict):
                    def to(self, device):
                        return self
                return Encoded({'input_ids': [0]})
            def decode(self, tokens, skip_special_tokens=True):
                return 'text'
            def to(self, device):
                return self
        return Tok()
