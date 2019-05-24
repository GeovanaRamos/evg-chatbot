import logging
import os

from rasa_core.utils import configure_colored_logging, AvailableEndpoints
from rasa_core.run import start_server, load_agent
from rasa_core.interpreter import NaturalLanguageInterpreter

from connector import RocketChatInput

logger = logging.getLogger(__name__)
configure_colored_logging(loglevel='DEBUG')


def run(core_dir, nlu_dir):
    configs = {
        'user': os.getenv('ROCKETCHAT_USER', 'bot'),
        'password': os.getenv('ROCKETCHAT_PASSWORD', 'bot'),
        'server_url': os.getenv('ROCKETCHAT_URL', 'http://localhost:3000'),
    }

    port = int(os.getenv('PORT', 5005))

    input_channel = RocketChatInput(
        user=configs['user'],
        password=configs['password'],
        server_url=configs['server_url'],
    )

    _endpoints = AvailableEndpoints.read_endpoints(None)
    _interpreter = NaturalLanguageInterpreter.create(nlu_dir)

    _agent = load_agent(core_dir,
                        interpreter=_interpreter,
                        endpoints=_endpoints)

    http_server = start_server([input_channel], "", "", port, _agent)
    
    try:
        http_server.serve_forever()
    except Exception as exc:
        logger.exception(exc)


if __name__ == '__main__':
    run('models/current/dialogue', 'models/current/nlu')
