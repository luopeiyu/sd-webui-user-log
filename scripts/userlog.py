import os
import time
import datetime
import modules.scripts as scripts
import modules.shared as shared
from modules.shared import opts, cmd_opts, state
import modules.script_callbacks as script_callbacks
from fastapi import FastAPI, Request
import gradio as gr
import modules

user_log_request_ip = "0.0.0.0"
user_log_cookie_user = ""




class PostprocessImageArgs:
    def __init__(self, image):
        self.image = image

class Script(scripts.Script):
    def __init__(self) -> None:
        super().__init__()
        self.logfile = "log/user.log"
        if not os.path.exists("log"):
            os.mkdir("log")

    def title(self):
        return "User Log"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def get_model_name(self):
        model_name = ("" if not opts.add_model_name_to_info or not shared.sd_model.sd_checkpoint_info.model_name else shared.sd_model.sd_checkpoint_info.model_name.replace(
            ',', '').replace(':', ''))
        return model_name

    def get_processing_tpye(self, p):
        if type(p) == modules.processing.StableDiffusionProcessingImg2Img:
            return "Img2Img"
        elif type(p) == modules.processing.StableDiffusionProcessingTxt2Img:
            return "Txt2Img"
        else:
            return "Unknow"

    def postprocess(self, p, processed, *args):
        """
        This function is called after processing ends for AlwaysVisible scripts.
        args contains all values returned by components from ui()
        """
        timeStr = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(time.time() + 8*3600))
        model_name = self.get_model_name()
        ip = user_log_request_ip
        user = user_log_cookie_user
        processing_tpye = self.get_processing_tpye(p)

        n_iter = str(p.n_iter)
        batch_size = str(p.batch_size)

        text = "{timeStr},{ip},{user},{processing_tpye},{n_iter},{batch_size},{model_name}\n".format(
            timeStr=timeStr, model_name=model_name, ip=ip, user=user, processing_tpye=processing_tpye, n_iter=n_iter, batch_size=batch_size)

        print(text)

        with open(self.logfile, 'a') as f:
            f.write(text)
            f.flush()
            f.close()

        pass


    def postprocess_image(self, p, pp: PostprocessImageArgs, *args):
        """
        Called for every image after it has been generated.
        """
        pass





def on_app_started(demo: gr.Blocks, app: FastAPI):

    @app.middleware("http")
    async def get_client_info(request: Request, call_next):
        global user_log_request_ip
        global user_log_cookie_user

        user_log_request_ip = request.client.host
        user_log_cookie_user = "sh0000"

        user = request.cookies.get('user')
        if user != "":
            user_log_cookie_user = user

        response = await call_next(request)
        return response


script_callbacks.on_app_started(on_app_started)
