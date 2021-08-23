# -*- encoding: utf-8 -*-

{
    'name': 'Survey Attachment',
    'summary': """
        An easy way to attach a file to your survey. This functionality is realized through choosing the type of questions beforehand; then uploading the file.""",
    'version': '12.0',
    'category': 'Survey',
    'description': """
        Add attachment to survey
    """,
    'author': 'Fogits Solutions',
    'website': 'https://www.fogits.com/',
    'depends': ['survey'],
    'images': ['static/description/survey.jpg'],
    'data': [
        'views/survey_question_template.xml',
        'views/survey_user_input_line_view.xml',
    ],
}
