import random
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer, AutoModelForCausalLM

features_citrus_hfl_gemma = """
{
    "brix": {{data}},
    "tree height": {{data}},
    "scion survive": {{data}},
    "fruit harvest trait": {{data}},
    "number of branches": {{data}},
}
"""

# print(features_citrus_hfl_gemma)


tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it")

input_text = f"""<start_of_turn>user
Consider you are a JSON data extraction tool. You can only reply in JSON with the given format {features_citrus_hfl_gemma}
brix is often spelled as bricks
scion survive can be alive or dead
fruit harvest trait can be clean or plugged

Input: PROMPT_INPUT
<start_of_turn>model
"""
# input_text = "Hello"
input_ids = tokenizer(input_text, max_length=150, return_tensors="pt", truncation=True)

outputs = model.generate(**input_ids, max_new_tokens=200)
print(tokenizer.decode(outputs[0]))



# 
#
#



# models = [
#     "google/gemma-7b",
#     "google/gemma-7b-it",
#     "google/gemma-2b",
#     "google/gemma-2b-it"
# ]
# clients = [
#     InferenceClient(models[0]),
#     InferenceClient(models[1]),
#     InferenceClient(models[2]),
#     InferenceClient(models[3]),
# ]

# VERBOSE = False


# def load_models(inp):
#     if VERBOSE == True:
#         print(type(inp))
#         print(inp)
#         print(models[inp])
#     # client_z.clear()
#     # client_z.append(InferenceClient(models[inp]))
#     return gr.update(label=models[inp])


# def format_prompt(message, history, cust_p):
#     prompt = ""
#     if history:
#         for user_prompt, bot_response in history:
#             prompt += f"<start_of_turn>user{user_prompt}<end_of_turn>"
#             prompt += f"<start_of_turn>model{bot_response}<end_of_turn>"
#             if VERBOSE == True:
#                 print(prompt)
#     # prompt += f"<start_of_turn>user\n{message}<end_of_turn>\n<start_of_turn>model\n"
#     prompt += cust_p.replace("USER_INPUT", message)
#     return prompt


# def chat_inf(system_prompt, prompt, history, memory, client_choice, seed, temp, tokens, top_p, rep_p, chat_mem, cust_p):
#     # token max=8192
#     print(client_choice)
#     hist_len = 0
#     client = clients[int(client_choice)-1]
#     if not history:
#         history = []
#         hist_len = 0
#     if not memory:
#         memory = []
#         mem_len = 0
#     if memory:
#         for ea in memory[0-chat_mem:]:
#             hist_len += len(str(ea))
#     in_len = len(system_prompt+prompt)+hist_len

#     if (in_len+tokens) > 8000:
#         history.append(
#             (prompt, "Wait, that's too many tokens, please reduce the 'Chat Memory' value, or reduce the 'Max new tokens' value"))
#         yield history, memory
#     else:
#         generate_kwargs = dict(
#             temperature=temp,
#             max_new_tokens=tokens,
#             top_p=top_p,
#             repetition_penalty=rep_p,
#             do_sample=True,
#             seed=seed,
#         )
#         if system_prompt:
#             formatted_prompt = format_prompt(
#                 f"{system_prompt}, {prompt}", memory[0-chat_mem:], cust_p)
#         else:
#             formatted_prompt = format_prompt(
#                 prompt, memory[0-chat_mem:], cust_p)
#         stream = client.text_generation(
#             formatted_prompt, **generate_kwargs, stream=True, details=True, return_full_text=True)
#         output = ""
#         for response in stream:
#             output += response.token.text
#             yield [(prompt, output)], memory
#         history.append((prompt, output))
#         memory.append((prompt, output))
#         yield history, memory

#     if VERBOSE == True:
#         print("\n######### HIST "+str(in_len))
#         print("\n######### TOKENS "+str(tokens))


# def get_screenshot(chat: list, height=5000, width=600, chatblock=[], theme="light", wait=3000, header=True):
#     print(chatblock)
#     tog = 0
#     if chatblock:
#         tog = 3
#     result = ss_client.predict(
#         str(chat), height, width, chatblock, header, theme, wait, api_name="/run_script")
#     out = f'https://omnibus-html-image-current-tab.hf.space/file={result[tog]}'
#     print(out)
#     return out


# def clear_fn():
#     return None, None, None, None


# rand_val = random.randint(1, 1111111111111111)


# def check_rand(inp, val):
#     if inp == True:
#         return gr.Slider(label="Seed", minimum=1, maximum=1111111111111111, value=random.randint(1, 1111111111111111))
#     else:
#         return gr.Slider(label="Seed", minimum=1, maximum=1111111111111111, value=int(val))


# with gr.Blocks() as app:
#     memory = gr.State()
#     gr.HTML("""<center><h1 style='font-size:xx-large;'>Google Gemma Models</h1><br><h3>running on Huggingface Inference Client</h3><br><h7>EXPERIMENTAL""")
#     chat_b = gr.Chatbot(height=500)
#     with gr.Group():
#         with gr.Row():
#             with gr.Column(scale=3):
#                 inp = gr.Textbox(label="Prompt")
#                 sys_inp = gr.Textbox(label="System Prompt (optional)")
#                 with gr.Accordion("Prompt Format", open=False):
#                     custom_prompt = gr.Textbox(label="Modify Prompt Format", info="For testing purposes. 'USER_INPUT' is where 'SYSTEM_PROMPT, PROMPT' will be placed",
#                                                lines=3, value="<start_of_turn>userUSER_INPUT<end_of_turn><start_of_turn>model")
#                 with gr.Row():
#                     with gr.Column(scale=2):
#                         btn = gr.Button("Chat")
#                     with gr.Column(scale=1):
#                         with gr.Group():
#                             stop_btn = gr.Button("Stop")
#                             clear_btn = gr.Button("Clear")
#                 client_choice = gr.Dropdown(label="Models", type='index', choices=[
#                                             c for c in models], value=models[0], interactive=True)
#             with gr.Column(scale=1):
#                 with gr.Group():
#                     rand = gr.Checkbox(label="Random Seed", value=True)
#                     seed = gr.Slider(
#                         label="Seed", minimum=1, maximum=1111111111111111, step=1, value=rand_val)
#                     tokens = gr.Slider(label="Max new tokens", value=1600, minimum=0, maximum=8000,
#                                        step=64, interactive=True, visible=True, info="The maximum number of tokens")
#                     temp = gr.Slider(label="Temperature", step=0.01,
#                                      minimum=0.01, maximum=1.0, value=0.49)
#                     top_p = gr.Slider(label="Top-P", step=0.01,
#                                       minimum=0.01, maximum=1.0, value=0.49)
#                     rep_p = gr.Slider(
#                         label="Repetition Penalty", step=0.01, minimum=0.1, maximum=2.0, value=0.99)
#                     chat_mem = gr.Number(
#                         label="Chat Memory", info="Number of previous chats to retain", value=4)
#         with gr.Accordion(label="Screenshot", open=False):
#             with gr.Row():
#                 with gr.Column(scale=3):
#                     im_btn = gr.Button("Screenshot")
#                     img = gr.Image(type='filepath')
#                 with gr.Column(scale=1):
#                     with gr.Row():
#                         im_height = gr.Number(label="Height", value=5000)
#                         im_width = gr.Number(label="Width", value=500)
#                     wait_time = gr.Number(label="Wait Time", value=3000)
#                     theme = gr.Radio(label="Theme", choices=[
#                                      "light", "dark"], value="light")
#                     chatblock = gr.Dropdown(label="Chatblocks", info="Choose specific blocks of chat", choices=[
#                                             c for c in range(1, 40)], multiselect=True)

#     client_choice.change(load_models, client_choice, [chat_b])
#     app.load(load_models, client_choice, [chat_b])

#     im_go = im_btn.click(get_screenshot, [
#                          chat_b, im_height, im_width, chatblock, theme, wait_time], img)

#     chat_sub = inp.submit(check_rand, [rand, seed], seed).then(chat_inf, [
#         sys_inp, inp, chat_b, memory, client_choice, seed, temp, tokens, top_p, rep_p, chat_mem, custom_prompt], [chat_b, memory])
#     go = btn.click(check_rand, [rand, seed], seed).then(chat_inf, [sys_inp, inp, chat_b, memory,
#                                                                    client_choice, seed, temp, tokens, top_p, rep_p, chat_mem, custom_prompt], [chat_b, memory])

#     stop_btn.click(None, None,None,cancels=[go,im_go,chat_sub])
#     clear_btn.click(clear_fn, None,[inp,sys_inp,chat_b,memory])
# app.queue(default_concurrency_limit=10).launch()
