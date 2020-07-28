import prodigy
from prodigy.components.loaders import JSONL
from prodigy.components.preprocess import fetch_images

def add_options(stream):
    # Helper function to add options to every task in a stream
    options = [
        {"id": "0", "text": "missing classification"},
        {"id": "-", "text": "wrong classification"},
        {"id": "o", "text": "area is overestimated"},
        {"id": "u", "text": "area is underestimated"},
    ]
    for task in fetch_images(stream):
        task["options"] = options
        yield task

@prodigy.recipe('image_recipe')
def image_recipe(dataset, source):
    num_lines = sum(1 for line in open(source))
    def progress(session, total):
        '''
        Shows your progress 
        '''
        return total / num_lines
    stream = JSONL(source)
    stream = add_options(stream)
    
    return {
        'dataset': dataset,          # ID of dataset to store annotations
        'stream': stream,     #  stream of examples
        'progress': progress,  # annotation progress
        'view_id': 'choice',           # annotation interface
        'config': {"choice_style": "multiple",
                   "instructions" : "config/serp-help.html"} 
    }