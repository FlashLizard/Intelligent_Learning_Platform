from AIPPT_app import AIPPT


def generate_ppt(file_name, theme, is_card_note):
    text = "请根据这段文字，生成一个教学所用的ppt"

    selected_file_name = file_name
    theme = theme

    is_card_note = is_card_note

    APPId = "e76d7d8f"
    APISecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"

    # 创建AIPPT类的实例并处理PPT
    demo = AIPPT(APPId, APISecret, text)
    demo.get_result(theme=theme, is_card_note=is_card_note, selected_file_name=selected_file_name)
