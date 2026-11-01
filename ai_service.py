# Explainable baseline triage. Replace/extend this module with trained YOLO inference.
# No trained neural-network weights are bundled, so this module does NOT claim object detection.
KEYWORDS={
 "Pothole":(["deep","large","accident","danger","vehicle"],"Roads & Public Works"),
 "Streetlight":(["dark","night","broken","not working","unsafe"],"Electrical Services"),
 "Garbage":(["overflow","smell","waste","dump","rats"],"Sanitation Department"),
 "Water leakage":(["flood","burst","leaking","water","pipe"],"Water Works"),
 "Open manhole":(["open","missing cover","manhole","fall","danger"],"Roads & Public Works"),
 "Damaged footpath":(["broken","cracked","blocked","pedestrian"],"Roads & Public Works"),
}
def analyse(category:str,description:str):
    text=description.lower()
    keywords,department=KEYWORDS.get(category,([], "Municipal Services"))
    score=sum(1 for word in keywords if word in text)
    critical_terms=("electrocution","open manhole","major flood","accident","injury","fire")
    high_terms=("deep","large","overflow","danger","blocked","burst")
    severity="CRITICAL" if any(w in text for w in critical_terms) else "HIGH" if score>=2 or any(w in text for w in high_terms) else "MEDIUM"
    priority="CRITICAL" if severity=="CRITICAL" else "HIGH" if severity=="HIGH" else "MEDIUM"
    reason=f"Baseline text triage: category={category}; matched {score} category keywords. Severity is a preliminary suggestion and requires officer verification."
    return {"department":department,"severity":severity,"priority":priority,"ai_reason":reason}
