import os
import gradio as gr
import time
from groq import Groq
from faster_whisper import WhisperModel

# Tutorials followed to build this chatbot include: https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks

# set up groq client
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"), )

recipe_response = ""
recipes_list = []

css = """
            body {
            font-family: Inconsolata, Arial, sans-serif;
            }
            .gradio-container {
                background-color: #F0F0DC
            }
            #RecipeBot {
                background-color: white;
                color: white;
            }
            textarea::placeholder {
                font-size: 18px;
            }
            #custom_recipe textarea::placeholder {
                font-size: 14px;
            }
            .toggle-button {
                background-color:  rgb(132, 204, 22) !important;
                border-bottom-color: white !important ;
                border-left-color: white !important ;
                border-right-color: white !important;
                border-top-color: white !important ;
                color: black !important ;
            }
 """

translations = {
    "English": {
        "greeting": "<h1 style=\"text-align:center; color:black; font-size:32px;\"> 🍳 Welcome to RecipeBot! What kind of recipe are you looking for? 🍳</h1>",
        "placeholder": "Need a recipe? Type or record your request here!",
        "langugage_dropdown": "Language",
        "language_dropdown_description": "Choose RecipeBot language",
        "language_choices":["English", "Francais"],
        "units_dropdown": "Measurement units",
        "units_dropdown_description":"Choose recipe measurement units",
        "units_choices": ["Metric", "Imperial"],
        "diet_dropdown": "Diet type",
        "diet_choices":["None", "Vegetarian", "Vegan", "Gluten-free", "Halal", "Kosher"],
        "save": "Save recipe",
        "sidebar_title": "<h3>Saved Recipes</h3>",
        "clear_recipes": "Clear saved recipes",
        "options_title": "<h3>RecipeBot Settings</h3>",
        "custom_recipe": "<h3 style=\" /*text-align:center;*/ color:black; font-size:18px; \">Want a custom recipe? Enter the ingredients you want and don't want below, and RecipeBot will make one for you!</h3>",
        "custom_recipe_include": "Enter ingredients you want included in the recipe here",
        "custom_recipe_exclude": "Enter ingredients you want excluded in the recipe here",
        "custom_recipe_submit": "Create custom recipe",
        "include_label": "Ingredients to include",
        "exclude_label": "Ingredients to exclude",
        "chatbot_initial_message": "Hi there! Ask me for a recipe!",
        "custom_recipe_clear": "Clear inputs",
        
    },
    "Francais": {
        "greeting": "<h1 style=\"text-align:center; color:black; font-size:32px\"> 🍳 Bienvenue à RecipeBot ! Quel type de recette recherchez-vous ? 🍳</h1>",
        "placeholder": "Besoin d'une recette ? Tapez ou enregistrez votre demande ici !",
        "langugage_dropdown": "Langue",
        "language_dropdown_description": "Sélectionner la langue",
        "language_choices":["English", "Francais"],
        "units_dropdown": "Unités de mesure",
        "units_dropdown_description":"Choisissez les unités de mesure de la recette",
        "units_choices": ["Métrique", "Impérial"],
        "diet_dropdown": "Type de régime",
        "diet_choices": ["Aucun", "Végétarien", "Végétalien", "Sans gluten", "Halal", "Kascher"],
        "save": "Sauvegarder la recette",
        "sidebar_title": "<h3>Recettes Sauvegardées</h3>",
        "clear_recipes": "Effacer les recettes enregistrées",
        "options_title": "<h3>Paramètres de RecipeBot</h3>",
        "custom_recipe": "<h3 style=\"/*text-align:center;*/ color:black; font-size:18px;\">Vous voulez une recette personnalisée ? Entrez les ingrédients que vous voulez et ceux que vous ne voulez pas, et RecipeBot en fera une pour vous ! </h3>",
        "custom_recipe_include": "Entrez les ingrédients que vous voulez inclure dans la recette ici",
        "custom_recipe_exclude": "Entrez les ingrédients que vous voulez exclure dans la recette ici",
        "custom_recipe_submit": "Créer une recette personnalisée",
        "include_label": "Ingrédients à inclure",
        "exclude_label": "Ingrédients à exclure",
        "chatbot_initial_message": "Salut! Demande-moi une recette!",
        "custom_recipe_clear": "Effacer les entrées"
    }
}

# system_prompt
system_role =  {
            "role": "system",
            "content": """You are an expert recipe assistant and knowledgeable about every cuisine. 
                        You will answer in the same the language used by the user. 
                        Do not mention that your response will be tailored to the provided 
                        units or the user\'s language. Use the measurement units provided in the user input. 
                        Make sure the recipe respects the use's diet. If the inputted Diet is "None", then the user does not have any dietary restrictions. If the 
                        inputted Diet is "None", do not mention that the user has no dietary restrictions.
                        Inlcude a follow-up question, in the interface language, related to the recipe in the form "Is there..." but if the user 
                        is finished with the interaction, the follow-up question should ask if there is anything else you can help with.
                        For any ambiguous input or input unrelated to recipes, do not assume what the user means but instead ask a clarifying question
                        to guide the user to providing an input related to a recipe - this clarifying answer should not contain a recipe. Do not entertain the unrelated input.    
                        If the user asks for a recipe to be generated after providing ingredients to include and exclude, start your recipe with something along the lines of 
                        'Here is your custom recipe' in the interface language. You must include all included ingredients and exlcude all excluded ingredients. If some or all of the igredients included are not actual food items, seek clarification from the user.
                        If there is a contradiciton between included and excluded ingredients, seek clarification.
                        """
}

# initialize chat history
chat_history = [system_role]

def change_language(language):
    translation = translations[language]
    return (
        gr.HTML(value=translation["greeting"]),
        gr.Chatbot(elem_id="RecipeBot", type="messages",value=[{"role":"assistant", "content":translation["chatbot_initial_message"]}]),
        gr.MultimodalTextbox(
            interactive=True,
            placeholder=translation["placeholder"],
            show_label=False,
            sources=["microphone"],
        ),
        gr.Dropdown(
            choices=translation["language_choices"],
            value=language,
            interactive=True,
            label=translation["langugage_dropdown"],
           # info=translation["language_dropdown_description"]
        ),
        gr.Dropdown(
            choices=translation["units_choices"],
            value=translation["units_choices"][0],
            type="value",
            label=translation["units_dropdown"],
          #  info=translation["units_dropdown_description"],
            interactive=True
        ),
        gr.Dropdown(
            choices=translation["diet_choices"],
            value=translation["diet_choices"][0],
            type="value",
            label=translation["diet_dropdown"],
           # info=translation["units_dropdown_description"],
            interactive=True
        ),
        gr.Button(value=translation["save"]),
        gr.HTML(value=translation["sidebar_title"]),
        gr.Button(value=translation["clear_recipes"]),
        gr.HTML(value=translation["options_title"]),
        gr.HTML(translation["custom_recipe"]),
        gr.Textbox(label=translation["include_label"], placeholder=translation["custom_recipe_include"], elem_id="custom_recipe", interactive=True),
        gr.Textbox(label=translation["exclude_label"], placeholder=translation["custom_recipe_exclude"], elem_id="custom_recipe", interactive=True),
        gr.Button(value=translation["custom_recipe_submit"]),
        gr.Button(value=translation["custom_recipe_clear"])


    )

def get_response(user_input, units, diet):
    global chat_history
    user_input = user_input + " Measurement units: " + units + " Diet: " + diet
    print(user_input)
    print("******************")

    # append user input
    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(model="llama-3.3-70b-versatile",
                                                messages= chat_history,
                                                temperature=0.35,
                                                max_completion_tokens=1024,
                                                top_p=0.5,
                                                stream=False,
                                                stop=None)   
    
    response_content = response.choices[0].message.content
   # print(response_content)

    # append assistant response
    chat_history.append({"role":"assistant", 
                         "content": response_content
    })

    global recipe_response
    recipe_response = response_content
    
    return response_content

def transcribe_audio(audio_file, lang_code="en"):
    output = ""
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio=audio_file, language=lang_code, beam_size=5)
        for segment in segments:
            output += segment.text + " "
        return output
    except Exception as e:
        return None, str(e)
    

def add_message(history, message, is_custom=False, include="", exclude=""):
    if(not is_custom):
        for audio in message["files"]:
            transcription = transcribe_audio(audio)
            history.append({"role": "user", "content": transcription})
        if message["text"] is not None and message["text"] != "":
            history.append({"role": "user", "content":message["text"]})

    else:
        if(message is not None and message != ""):
            history.append({"role": "user", "content":message})
    
    return history, gr.MultimodalTextbox(value=None, interactive=False)

def bot(history, units, diet):
    response = get_response(history[-1]["content"], units, diet)
    history.append({"role": "assistant", "content": ""})
    for character in response:
        history[-1]["content"] += character
        time.sleep(0.002)
        yield history

def generate_title(recipe):
    if(recipe != "") :
        title = ""
        user_input = "Give a title for this recipe in 3 words only. If it is not a recipe, your answer should be exactly 'Not a recipe'. If the recipe is in french, give the title in french. Your output should only contain the title: \n" + recipe
        i = [{"role": "user", "content": user_input}]

        response = client.chat.completions.create(model="llama-3.3-70b-versatile",
                                                    messages= i,
                                                    temperature=0.35,
                                                    max_completion_tokens=1024,
                                                    top_p=0.5,
                                                    stream=False,
                                                    stop=None)   
        
        title = response.choices[0].message.content
        print("Title:")
        print(title)
        return title
    return

def keep_recipe():
    if(recipe_response != ""):
        global recipes_list
        recipe = recipe_response
        recipe_title = generate_title(recipe_response)
        if(recipe_title != "Not a recipe"):
            for r in recipes_list:
                if ( r["title"] == recipe_title):
                    r["title"] = "DELETE"

            recipes_list = [recipe for recipe in recipes_list if recipe["title"] != "DELETE"]
            
            recipe_obj = {
                "title": recipe_title,
                "recipe": recipe
            }
            recipes_list.append(recipe_obj)
        
            return update_sidebar()
    return update_sidebar()

def update_sidebar():
    sidebar_content = ""
    if len(recipes_list) > 0:
        vis=True
        sidebar_content += "<ul style='margin: 0; padding: 0;'>"
        for recipe in recipes_list:
            filename = recipe['title'].replace(" ", "-") + ".txt"
            filecontent = recipe['recipe']
            print(filename)
            sidebar_content += f"""<li><b>{recipe['title']}</b> - <a href="data:text/plain;charset=utf-8,{filecontent}" download={filename}>Download</a></li>"""
        sidebar_content += "</ul>"
    else:
        sidebar_content += "<div style='margin: 0; padding: 0;'></div>"
        vis=False
    return gr.HTML(sidebar_content, visible=vis)

def clear_saved_recipes():
    global recipes_list
    recipes_list = []
    return update_sidebar()

def generate_custom_recipe(include, exclude,chatbot, language, chat_input):
    if(language == "English"):
        user_input = """Generate a recipe for me! \n Ingredients to include: \n""" + include + """ \nIngredients to exclude: \n""" + exclude
    else:
        user_input = """Générer une recette pour moi! \n Ingrédients à inclure: \n""" + include + """\nIngrédients à exclure: \n""" + exclude
    return add_message(chatbot, user_input, True, include, exclude)

def toggle_generate_recipe(include, exclude):
    include = include.strip()
    exclude = exclude.strip()
    return gr.update(interactive=bool(include or exclude))

def clear_inputs():
    return "", ""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="lime", font=[gr.themes.GoogleFont("Inconsolata"), "Arial", "sans-serif"]), css=css) as demo:
    welcome_msg_html = gr.HTML(translations["English"]["greeting"])

    chatbot = gr.Chatbot(elem_id="RecipeBot", type="messages",value=[{"role":"assistant", "content":translations["English"]["chatbot_initial_message"]}])

    chat_input = gr.MultimodalTextbox(
        interactive=True,
        placeholder=translations["English"]["placeholder"],
        show_label=False,
        sources=["microphone"],
    )

    with gr.Column():
        custom_recipe = gr.HTML(translations["English"]["custom_recipe"])
        with gr.Group():
            with gr.Row():
                include = gr.Textbox(label="Ingredients to include", interactive=True, placeholder=translations["English"]["custom_recipe_include"], elem_id="custom_recipe")
                exclude = gr.Textbox(label="Ingredients to exclude", interactive=True, placeholder=translations["English"]["custom_recipe_exclude"], elem_id="custom_recipe")
            with gr.Row():
                clear_button = gr.Button(value=translations["English"]["custom_recipe_clear"], scale=1)  # Add Clear button
                generate_recipe = gr.Button(value=translations["English"]["custom_recipe_submit"], interactive=False, scale=3)

            include.change(toggle_generate_recipe, [include, exclude], generate_recipe)
            exclude.change(toggle_generate_recipe,[include, exclude], generate_recipe)

            clear_button.click(clear_inputs, [], [include, exclude])

    with gr.Sidebar(open=True, width=320, elem_id="sidebar"):
        with gr.Column():
            options = gr.HTML(translations["English"]["options_title"])
            language_select = gr.Dropdown(
                choices=translations["English"]["language_choices"],
                value="English",
                interactive=True,
                label=translations["English"]["langugage_dropdown"],
            )

            units_radio = gr.Dropdown(
                choices=translations["English"]["units_choices"],
                value="Metric",
                #type="value",
                label=translations["English"]["units_dropdown"],
                interactive=True
            )

            diet_select = gr.Dropdown(
                choices=translations["English"]["diet_choices"],
                value="None",
                label=translations["English"]["diet_dropdown"],
                interactive=True
            )
        with gr.Column():
            sidebar_title = gr.HTML(translations["English"]["sidebar_title"])
            updated_sidebar = gr.HTML(update_sidebar)
            clear_recipes = gr.Button(value="Clear saved recipes")
        clear_recipes.click(fn=clear_saved_recipes, outputs=updated_sidebar)
        
    with gr.Row():
        save_recipe = gr.Button(value=translations["English"]["save"])
        save_recipe.click(fn=keep_recipe, outputs=updated_sidebar)

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    

    bot_msg_1 = generate_recipe.click(fn=generate_custom_recipe, inputs=[include, exclude, chatbot, language_select, chat_input], outputs=[chatbot, chat_input])
    bot_msg_1 = bot_msg_1.then(bot, [chatbot, units_radio, diet_select], chatbot)
    bot_msg_1.then(lambda:gr.MultimodalTextbox(interactive=True), None, [chat_input] )

    bot_msg_2 = chat_msg.then(bot, [chatbot, units_radio, diet_select], chatbot)
    bot_msg_2.then(lambda:gr.MultimodalTextbox(interactive=True), None, [chat_input])

    language_select.change(
        fn=change_language,
        inputs=language_select,
        outputs=[welcome_msg_html, chatbot, chat_input, language_select, units_radio, diet_select, save_recipe, sidebar_title, clear_recipes, options,
                    custom_recipe, include, exclude, generate_recipe, clear_button
                 
                 ]
    )

demo.launch()