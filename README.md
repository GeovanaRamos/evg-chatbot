# EVG Rasa Bot

This is a Q&A bot made with Rasa Stack tools to answer students from EVG(Escola Virtual do Governo). It was built using [Rasa Starter Pack](https://github.com/RasaHQ/starter-pack-rasa-stack.git).



## Setup and installation

It is recommended that you run installation procedures inside a virtual environment. If you already have virtualenv installed just run

```
$ virtualenv -p python3.6 venv
```
And activate

```
$ source venv/bin/activate
```

If you haven’t installed Rasa NLU and Rasa Core yet, you can do it by navigating to the project directory and running:  
```
$ (venv) pip install -r requirements.txt
```

You also need to install a spaCy Portuguese language model. You can install it by running:

```
$ (venv) python -m spacy download pt
```

### Files for Rasa NLU model

- **data/nlu_data.md** file contains training examples of intents. One intent is a set of sentences that the bot expects to receive from the user and means something especific. 

	
- **nlu_config.yml** file contains the configuration of the Rasa NLU pipeline. The pipeline for this project is tensorflow. 


### Files for Rasa Core model

- **data/stories.md** file contains some training stories which represent the conversations between a user and the assistant. In this file you may define bot actions for each intent or group of intents.
- **domain.yml** file describes the domain of the assistant which includes intents, entities, slots, templates and actions the assistant should be aware of.  
- **endpoints.yml** file contains the webhook configuration for custom action. This project does not have custom actions, so don't worry about this too much if you don't intend to make one.  
- **policies.yml** file contains the configuration of the training policies for Rasa Core model. Here you can set bot precision and trainig configuration.

## Runnning the bot
- NOTE: If running on Windows, you will either have to [install make](http://gnuwin32.sourceforge.net/packages/make.htm) or copy the following commands from the Makefile.
1. You can train the Rasa NLU model by running:  
```make train-nlu```  
This will train the Rasa NLU model and store it inside the `/models/current/nlu` folder of your project directory.

2. Train the Rasa Core model by running:  
```make train-core```  
This will train the Rasa Core model and store it inside the `/models/current/dialogue` folder of your project directory.

3. In a new terminal start the server for the custom action by running:  
```make action-server```  
This will start the server for emulating the custom action.

4. Test the assistant by running:  
```make cmdline```  
This will load the assistant in your terminal for you to chat.

