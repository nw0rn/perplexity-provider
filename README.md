# perplexity-provider

1. You need a PERPLEXITY_API_KEY configured and set as environment variable.

```
export PERPLEXITY_API_KEY=<your-api-key>
```
## Usage Example
```
gptscript --default-model='sonar-small-chat from https://github.com/nw0rn/perplexity-provider' examples/helloworld.gpt
```

## Development

Run using the following commands

```
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
./run.sh
```

