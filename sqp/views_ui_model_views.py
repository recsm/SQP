

from sqp.views_ui_utils import URL


def question_base(question):
    
    return {
            "id":                   question.id,
            "url":                  URL.question(question.id),
            "urlCodingHistory":     URL.question_coding_history(question.id),
            "itemId":               question.item.id,
            "studyId":              question.item.study.id,
            "languageIso"  :        question.language.iso,
            "countryIso"  :         question.country.iso,
            "studyName":            question.item.study.name,
            "itemPart":             question.item.main_or_supplementary(),
            "itemCode":             question.item.admin,
            "itemName" :            question.item.name,  
            "country":              question.country.name,
            "countryIso":           question.country.iso,
            "language":             question.language.name,
            "itemDescription":      question.item.concept,
            "hasMTMM":              question.rel
            
            }