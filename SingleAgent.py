# -*- coding: utf-8 -*-

"""
@author: xansar
@software: PyCharm
@file: SingleAgent.py
@time: 2023/9/25 18:14
@e-mail: xansar@ruc.edu.cn
"""
import functools
from collections import OrderedDict
from typing import List

from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)

import os
os.environ["OPENAI_API_KEY"] = "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"
import re
import dill

from agents import DialogueAgent, DialogueSimulator
from metrics import Metrics
from medications import drug_lst
from utils import construct_med_map_dict

class SingleAgent:
    def __init__(self, model, drug_lst, med_map, word_limit=50):
        self.model = model
        self.word_limit = word_limit
        self.general_prompt = f"NEVER say the same things over and over again!!!. Speak in the first person from the " \
                              f"perspective of your role. For describing your own body movements, wrap your " \
                              f"description in '*'. Do not change roles! Do not speak from the perspective of anyone " \
                              f"else. Speak only from the perspective of your role. Stop speaking the moment you " \
                              f"finish speaking from your perspective. Never forget to keep your response to " \
                              f"{word_limit} words! Do not add anything else. " \
                              f'Please note that this is a virtual healthcare environment, and you cannot consider ' \
                              f'any specific time, people\'s name or location details during the conversation. ' \
                              f'NEVER NEVER CHANGE ROLES!!! NEVER NEVER SPEAK IN OTHER ROLES!!!'
        self.drug_lst = drug_lst
        self.med_map = med_map

    def patient_simulate(self, syms):
        patient_prompt = (
            'As a patient at SimuMed, your role is vital in the healthcare process. '
            'Describe your symptoms accurately based on the [Symptoms], engage in open communication, '
            'and actively participate in discussions to achieve the best possible medical outcomes.'
            "In the upcoming conversation, you will interact with the primary physician."
            "It is crucial to provide a detailed description of your health condition and symptoms."
            "Please make sure to inform the doctor about all your symptoms, including any discomfort, persistent issues,"
            "and possible triggering factors. Offering accurate information helps the doctor make the right diagnosis"
            "and create an effective treatment plan."
            "Please be open and honest in sharing your symptoms during the conversation and respond to any questions"
            "the doctor may ask. Only through a comprehensive understanding can the doctor provide you with the best"
            "medical advice and treatment plan."
        )
        patient_prompt += '[Symptoms]:\n\n' + syms + '\n\n'
        return DialogueAgent(
            name='Patient',
            system_message=SystemMessage(content=patient_prompt + self.general_prompt),
            model=self.model
        )

    def doctor_simulate(self):
        doctor_prompt = (
            "As the attending physician at SimuMed, your role is crucial in assessing patients and providing appropriate treatment. "
            "In the upcoming conversation, you will act as a physician. Your primary task is to inquire about the patient's symptoms. "
            "Please ask the patient to provide their symptoms. Once you have gathered all the relevant symptoms, "
            "summarize them and formulate a diagnosis for the patient. "
            "Feel free to end the conversation with 'TERMINATE' when you believe there are no more questions or concerns from either party."
        )
        return DialogueAgent(
                    name='Doctor',
                    system_message=SystemMessage(content=doctor_prompt + self.general_prompt),
                    model=self.model
                )

    def _run_dial(self, dial_simulator):
        dial_simulator.reset()
        dial_simulator.inject('System', 'Begin Conversation.')
        while True:
            name, message = dial_simulator.step()
            print(f"({name}): {message}")
            print('')
            if 'TERMINATE' in message:
                break
    @staticmethod
    def _speak_in_turn(step, agents):
        return (step + 1) % len(agents)

    @staticmethod
    def _set_dial_simulator(agents, speaker_select_func):
        return DialogueSimulator(agents=agents, selection_function=speaker_select_func)

    @staticmethod
    def parse_medications(raw_medications_text):
        pattern = r'\b[A-Z][0-9]{2}[A-Z]\b'
        codes = re.findall(pattern, raw_medications_text)
        return codes

    def diagnose(self, chat_history):
        response_shemas = [
            ResponseSchema(name='diagnoses', description='the diagnoses for the patient'),
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_shemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    'You are a doctor and you have chatted with your patient just now. Conclude the conversation history and get the diagnoses for the patient: {conversation_history}\n\n'
                    '\n{format_instructions}\n'
                )
            ],
            input_variables=["conversation_history"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format_prompt(conversation_history=''.join(chat_history))
        output = self.model(_input.to_messages())
        output = output_parser.parse(output.content)
        diagnoses = output['diagnoses']
        print(diagnoses)
        return diagnoses


    def recommend_meds(self, diagnoses):
        response_shemas = [
            ResponseSchema(name='medications', description='the recommended medications for the patient')
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_shemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    'You are a doctor and you have diagnosed your patient just now. Your diagnoses are {diagnoses}. '
                    "Based on the diagnosis and considering potential drug interactions (DDIs), recommend a limited list of medications from "
                    "the provided [DrugList] that are essential for the patient's treatment. Avoid recommending excessive medications or missing "
                    "important ones. Your goal is to provide a precise and effective treatment plan."
                    '\n[DrugList]: {drug_lst}.\n'
                    'The mediations list should contain the corresponding indices of the medications like "129. V04C". Y'
                    '\n{format_instructions}\n'
                )
            ],
            input_variables=["diagnoses", "drug_lst"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format_prompt(diagnoses=diagnoses, drug_lst=self.drug_lst)
        raw_output = self.model(_input.to_messages())
        output = output_parser.parse(raw_output.content)

        medications = output['medications']
        med_codes = self.parse_medications(str(medications))
        print(med_codes)
        return med_codes

    def simulate(self, syms):
        patient = self.patient_simulate(syms)
        doctor = self.doctor_simulate()
        agents = [doctor, patient]
        dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
        self._run_dial(dial_simulator)
        print(patient.message_history)

        chat_history = patient.message_history
        diagnoses = self.diagnose(chat_history)

        # chat_history = ['Here is the conversation so far.', 'System: Begin Conversation.', 'Doctor: Hello, I am Dr. Smith, the attending physician at SimuMed. How can I assist you today?', 'Patient: I have been experiencing respiratory distress, cough, and shortness of breath. I also have fatigue, myalgias, and night sweats. Additionally, I have been feeling nauseous and have had a rash.', 'Doctor: Have you noticed any fever or chills along with these symptoms?', 'Patient: No, I am afebrile and have not experienced any chills.', 'Doctor: Have you traveled recently or been in contact with anyone who has traveled to areas with high rates of infectious diseases?', 'Patient: No, I have not traveled recently or been in contact with anyone who has traveled to areas with high rates of infectious diseases.', 'Doctor: Have you had any recent exposure to chemicals or allergens that could potentially cause respiratory symptoms or a rash?', 'Patient: No, I have not had any recent exposure to chemicals or allergens that could potentially cause respiratory symptoms or a rash.', 'Doctor: Have you noticed any changes in your appetite or weight loss?', 'Patient: No, I have not noticed any changes in my appetite or experienced weight loss.', 'Doctor: Have you had any chest pain or tightness in your chest along with these symptoms?', 'Patient: No, I have not experienced any chest pain or tightness in my chest along with these symptoms.', 'Doctor: Have you had any recent travel to areas with poor air quality or pollution?', 'Patient: No, I have not had any recent travel to areas with poor air quality or pollution.', 'Doctor: Based on the symptoms you have described, including respiratory distress, cough, shortness of breath, fatigue, myalgias, night sweats, nausea, and rash, it is important to consider a few possible diagnoses. One possibility could be a respiratory infection, such as pneumonia or bronchitis. Another possibility could be an allergic reaction, as you mentioned a rash and respiratory symptoms. It would also be important to rule out other potential causes, such as asthma or a viral illness. I recommend further evaluation and testing to determine the exact cause of your symptoms. TERMINATE']
        # diagnoses = 'Possible diagnoses include respiratory infection (such as pneumonia or bronchitis), allergic reaction, asthma, or viral illness. Further evaluation and testing are recommended to determine the exact cause of the symptoms.'

        chat_history = ['Here is the conversation so far.', 'System: Begin Conversation.', 'Doctor: Hello, I am Dr. Smith, the attending physician at SimuMed. How can I assist you today?', 'Patient: I have a wound on my thigh that is causing me a lot of pain. It is swollen and there is some drainage coming from it. I also have numbness in the area.', 'Doctor: When did you first notice the wound on your thigh? Is there any redness or warmth around the wound? Have you experienced any fever or chills?', 'Patient: I noticed the wound on my thigh a few days ago. There is some redness and warmth around the wound. However, I am afebrile and have not experienced any fever or chills.', 'Doctor: Are there any other symptoms you are experiencing? Have you noticed any changes in your appetite or energy levels? Any difficulty moving or walking?', 'Patient: I have also been experiencing shortness of breath and coughing. The cough is productive, and I have noticed some blood in my sputum. I have been feeling quite fatigued and have had poor intake of food.', "Doctor: Based on the patient's symptoms of a painful, swollen wound with drainage, numbness in the area, redness and warmth around the wound, along with shortness of breath, coughing with blood in the sputum, fatigue, and poor appetite, my initial diagnosis would be a possible infection in the wound with cellulitis and possible pneumonia. Further evaluation and testing would be necessary to confirm the diagnosis.", 'Patient: Yes, I understand. Thank you for your initial diagnosis. I am willing to undergo further evaluation and testing to confirm the diagnosis.', 'Doctor: TERMINATE']
        diagnoses = 'Possible infection in the wound with cellulitis and possible pneumonia'

        med_codes = self.recommend_meds(diagnoses)
        return med_codes


def main():
    med_map = construct_med_map_dict(drug_lst)
    ddi_matrix = dill.load(open('ddi_A_final.pkl', 'rb'))
    metric_scorer = Metrics(ddi_matrix, med_map)

    single_agent = SingleAgent(
        model=ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2, max_retries=100),
        drug_lst=drug_lst,
        med_map=med_map
    )

    # syms = "respiratory distress\nnausea\ncough\nchill\nshortness of breath\nsputum\npressure\nmyalgias\nfatigue\ndyspnea\nshort of breath\nafebrile\ntemperature\ndyspneic\nnight sweats\nrash\ntenderness\ntachycardia\ndehydrated\nfever\natelectasis\ncongestion\ninfection\nascites\nruq pain\nright upper quadrant pain\noriented\nawake\nwarm\ndiarrhea\nanxious\np.o. intake\nweak\nepistaxis"
    # label = ['R05D', 'P01B', 'A12B', 'N03A', 'A07E', 'D10A', 'H03A', 'N02B', 'B01A', 'A06A', 'A02B', 'D01A', 'D06B', 'A07A', 'B05C', 'J05A', 'A12C', 'A07D']

    syms = '\n'.join(['wound', 'thigh pain', 'numbness', 'anemia', 'pressure', 'good urine output',
                     'afebrile', 'hematoma', 'swollen', 'edema', 'swelling', 'pain', 'bleed',
                     'drainage', 'shortness of breath', 'atelectasis', 'leg swelling',
                     'temperature', 'emesis', 'nausea', 'hematuria', 'p.o. intake', 'cough',
                     'productive cough', 'oriented', 'poor po intake', 'asleep', 'warm', 'cool',
                     'awake', 'wheeze', 'blue', 'sputum'])
    label = ['A06A', 'A12C', 'L04A', 'C07A', 'C08C', 'D11A', 'C03C', 'N02B', 'B01A', 'R03A', 'A12A', 'A07E', 'A03F', 'J05A', 'B05C', 'N02A', 'A02B', 'D04A', 'A07A', 'J01E']

    for i in range(10):
        predictions = single_agent.simulate(syms)
        # predictions = ['R05D', 'A07A', 'A02A', 'A04A', 'R06A', 'J01F', 'J02A', 'J01A', 'J06B', 'R02A']
        metrics = metric_scorer.compute(predictions, label)
        print(metrics)


if __name__ == '__main__':
    main()

