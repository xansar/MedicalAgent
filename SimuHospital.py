# -*- coding: utf-8 -*-

"""
@author: xansar
@software: PyCharm
@file: SimuHospital.py
@time: 2023/9/20 19:00
@e-mail: xansar@ruc.edu.cn
"""
import functools
from collections import OrderedDict
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)

from agents import DialogueAgent, DirectorDialogueAgent, DialogueSimulator

import os

os.environ["OPENAI_API_KEY"] = "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"


class SimuHospital:
    def __init__(self, model, word_limit=50, patient_statement=None):
        super(SimuHospital, self).__init__()
        medical_departments = "1. Cardiology\n2. Neurology\n3. Oncology\n4. Dermatology\n5. Gastroenterology\n" \
                              "6. Orthopedic Surgery\n7. Endocrinology\n8. Pulmonology\n9. Rheumatology\n" \
                              "10. Urology\n11. Nephrology\n12. Hematology\n13. Gynecology\n14. Ophthalmology\n" \
                              "15. Otolaryngology (ENT)\n16. Pediatrics\n17. Urologic Surgery\n18. Cardiothoracic Surgery" \
                              "\n19. Hepatobiliary Surgery\n20. Neurosurgery\n21. Plastic Surgery\n22. Radiology\n" \
                              "23. Nuclear Medicine\n24. Rehabilitation Medicine\n25. Emergency Medicine\n" \
                              "26. Proctology\n27. Forensic Medicine\n28. Neurophysiology\n29. Pulmonary Function Testing\n" \
                              "30. Psychology\n31. Venereology\n32. Bariatrics"

        medical_specialties_and_doctors_lst = [
            ("Cardiology", "Cardiologist"),
            ("Neurology", "Neurologist"),
            ("Oncology", "Oncologist"),
            ("Dermatology", "Dermatologist"),
            ("Gastroenterology", "Gastroenterologist"),
            ("Orthopedic Surgery", "Orthopedic Surgeon"),
            ("Endocrinology", "Endocrinologist"),
            ("Pulmonology", "Pulmonologist"),
            ("Rheumatology", "Rheumatologist"),
            ("Urology", "Urologist"),
            ("Nephrology", "Nephrologist"),
            ("Hematology", "Hematologist"),
            ("Gynecology", "Gynecologist"),
            ("Ophthalmology", "Ophthalmologist"),
            ("Otolaryngology (ENT)", "Otolaryngologist"),
            ("Pediatrics", "Pediatrician"),
            ("Urologic Surgery", "Urologic Surgeon"),
            ("Cardiothoracic Surgery", "Cardiothoracic Surgeon"),
            ("Hepatobiliary Surgery", "Hepatobiliary Surgeon"),
            ("Neurosurgery", "Neurosurgeon"),
            ("Plastic Surgery", "Plastic Surgeon"),
            ("Radiology", "Radiologist"),
            ("Nuclear Medicine", "Nuclear Medicine Physician"),
            ("Rehabilitation Medicine", "Rehabilitation Medicine Physician"),
            ("Emergency Medicine", "Emergency Medicine Physician"),
            ("Proctology", "Proctologist"),
            ("Forensic Medicine", "Forensic Medicine Specialist"),
            ("Neurophysiology", "Neurophysiologist"),
            ("Pulmonary Function Testing", "Pulmonary Function Testing Specialist"),
            ("Psychology", "Psychologist"),
            ("Venereology", "Venereologist"),
            ("Bariatrics", "Bariatrician")
        ]

        self.departments = medical_departments
        self.departments_and_doctors_lst = medical_specialties_and_doctors_lst
        self.model = model
        self.patient = self.set_patient(patient_statement)
        self.nurse = self.set_nurse()
        self.pharmacist = self.set_pharmacist()
        self.word_limit = word_limit
        self.general_prompt = f"NEVER say the same things over and over again!!!. Speak in the first person from the " \
                              f"perspective of your role. For describing your own body movements, wrap your " \
                              f"description in '*'. Do not change roles! Do not speak from the perspective of anyone " \
                              f"else. Speak only from the perspective of your role. Stop speaking the moment you " \
                              f"finish speaking from your perspective. Never forget to keep your response to " \
                              f"{word_limit} words! Do not add anything else. " \
                              f"Feel free to end the conversation with 'TERMINATE' when you believe there are no more questions or concerns from either party." \
                              f'Please note that this is a virtual healthcare environment, and you cannot consider ' \
                              f'any specific time, people\'s name or location details during the conversation. ' \
                              f'NEVER NEVER CHANGE ROLES!!! NEVER NEVER SPEAK IN OTHER ROLES!!!'

    def set_patient(self, patient_statement):
        patient_prompt = \
            'As a patient at SimuMed, your role is vital in the healthcare process. ' \
            'Describe your symptoms accurately based on the [Patient Statement], engage in open communication, ' \
            'and actively participate in discussions to achieve the best possible medical outcomes.\n\n'
        patient_prompt += '[Patient Statement]:\n\n' + patient_statement + '\n\n'
        return DialogueAgent(
            name='Patient',
            system_message=SystemMessage(content=patient_prompt),
            model=self.model
        )

    def set_nurse(self):
        nurse_prompt = ''.join([
            f"As a Nurse at SimuMed, your primary role is to gather initial patient information and assign the patient to "
            f"the appropriate department within SimuMed based on their condition.",
            f"Your tasks only include conducting an initial assessment of the patient's condition and ensuring they are "
            f"directed to the relevant department at SimuMed for further evaluation and care. SimuMed offers a wide range "
            f"of specialized departments, including {self.departments}",
            f"Please focus on these tasks and provide the necessary information to ensure the patient receives the "
            f"appropriate care within our healthcare institution.\n\n"
        ])
        return DialogueAgent(
            name='Nurse',
            system_message=SystemMessage(content=nurse_prompt),
            model=self.model
        )

    def set_pharmacist(self):
        pharmacist_prompt = "As a pharmacist at SimuMed, your role is pivotal in ensuring medication safety and effectiveness. " \
                            "Review and refine prescriptions, provide patient-centered communication, " \
                            "and ensure patients comprehend their medications.py and treatments for safe and effective care.\n\n"
        return DialogueAgent(
            name='Pharmacist',
            system_message=SystemMessage(content=pharmacist_prompt),
            model=self.model
        )

    def set_doctor(self, role, specialization):
        doctor_prompt = f"As a {role} at SimuMed, you bring extensive expertise in {specialization}. " \
                        f"You'll play a crucial role, " \
                        f"diagnosing patients, prescribing treatments, and collaborating with other doctors, " \
                        f"ensuring top-quality care.\n\n"
        return DialogueAgent(
            name=role,
            system_message=SystemMessage(content=doctor_prompt),
            model=self.model
        )

    def set_director_primary_doctor(self, role, specialization, agents):
        doctor_prompt = f"As a {role} at SimuMed, you bring extensive expertise in {specialization}. " \
                        f"You'll play a crucial role, " \
                        f"diagnosing patients, prescribing treatments, and collaborating with other doctors, " \
                        f"ensuring top-quality care.\n\n"
        doctor_prompt += "As the primary physician, you lead this consultation, " \
                         "guiding discussions, summarizing diagnoses, " \
                         "and ensuring consensus among specialists. Engage the " \
                         "patient and facilitate unified decisions on diagnosis " \
                         "and treatment. Thank you for your vital role.\n\n"
        return DirectorDialogueAgent(
            name=f'{role}_as_PrimaryDoctor',
            system_message=SystemMessage(content=doctor_prompt),
            model=self.model,
            speakers=[ag.name for ag in agents],
            stopping_probability=0.2
        )

    @staticmethod
    def _speak_in_turn(step, agents):
        return (step + 1) % len(agents)

    @staticmethod
    def _speak_with_directed(step: int, agents: List[DialogueAgent], director: DirectorDialogueAgent) -> int:
        """
        If the step is even, then select the director
        Otherwise, the director selects the next speaker.
        """

        # the director speaks on odd steps
        if step % 2 == 1:
            idx = 0
        else:
            # here the director chooses the next speaker
            idx = director.select_next_speaker() + 1  # +1 because we excluded the director

        return idx

    @staticmethod
    def _set_dial_simulator(agents, speaker_select_func):
        return DialogueSimulator(agents=agents, selection_function=speaker_select_func)

    def _run_dial(self, dial_simulator):
        dial_simulator.reset()
        dial_simulator.inject('System', 'Begin Conversation.')
        while True:
            name, message = dial_simulator.step()
            print(f"({name}): {message}")
            print('')
            if 'TERMINATE' in message:
                break

    def _update_system_message(self, agent, addtional_msg):
        updated_msg = agent.system_message.content + addtional_msg
        agent.system_message = SystemMessage(content=updated_msg)
        return agent


    def nurse_triage_patient(self):
        # env prompt setting
        nurse_env_prompt = f"In the upcoming conversation, your role as a nurse is to lead the dialogue, initially " \
                           f"inquire about the patient's condition, and determine which department at SimuMed from [Departments] the " \
                           f"patient should be assigned to based on their preliminary information. Additionally, " \
                           f"please actively address any questions the patient may have. Provide support and " \
                           f"reassurance to ensure the patient feels comfortable and well-informed throughout this " \
                           f"medical process. Your role is crucial in ensuring the patient receives appropriate " \
                           f"medical care.\n\n[Departments]: {self.departments}"
        self.nurse = self._update_system_message(self.nurse, nurse_env_prompt + self.general_prompt)

        patient_env_prompt = "In the following conversation, your primary task is to describe your symptoms and " \
                             "answer any questions that the nurse may ask. Please be cooperative and provide clear " \
                             "information about your condition. If you have any questions or need clarification, " \
                             "feel free to ask the nurse for assistance. Your active participation is essential for a " \
                             "productive discussion.\n\n"
        self.patient = self._update_system_message(self.patient, patient_env_prompt + self.general_prompt)

        # set simulator
        agents = [self.nurse, self.patient]
        dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
        self._run_dial(dial_simulator)
        # _choose_primary_doctor(self):
        primary_doctor_idx = self.nurse.model([
            SystemMessage(
                content=f'Here is the conversation history. Conclude the conversation and choose which department in '
                        f'SimuMed is recommended from [Departments]. Make sure to include the chosen department in your summary. '
                        f'Return your selection as a Python list containing the numerical index of the recommended department. '
                        f'You need only reply with the list and do not say anything else. For example, if you choose Cardiology, '
                        f'your response should be: [1].\n\n[Departments]: {self.departments}\n\n'),
            HumanMessage(content=''.join(self.nurse.message_history))
        ]).content
        primary_doctor_field, primary_doctor_name = self.departments_and_doctors_lst[eval(primary_doctor_idx)[0] - 1]
        return primary_doctor_name, primary_doctor_field

    def doctor_treat_patient(self, primary_doctor_name, primary_doctor_field):
        self.primary_doctor = self.set_doctor(primary_doctor_name, primary_doctor_field)
        # reset_prompt
        self.patient.reset_prompt()
        # env prompt setting
        primary_doctor_env_prompt = "In the upcoming conversation, you will be assuming the role of the primary physician for the patient. " \
                                    "Your primary task is to inquire about the patient's medical condition and symptoms. " \
                                    "Based on the information provided by the patient, you will determine whether a " \
                                    "consultation with other specialists is necessary. At this stage, your focus is " \
                                    "on assessing the situation and deciding if a multi-specialty consultation is " \
                                    "required; you are not providing a diagnosis or prescription. " \
                                    "Your role is crucial in ensuring the patient receives the most appropriate care.\n\n"

        self.primary_doctor = self._update_system_message(self.primary_doctor, primary_doctor_env_prompt + self.general_prompt)

        patient_env_prompt = "In the following conversation, your primary task is to describe your symptoms and " \
                             "answer any questions that the doctor may ask. Please be cooperative and provide clear " \
                             "information about your condition. If you have any questions or need clarification, " \
                             "feel free to ask the doctor for assistance. Your active participation is essential for a " \
                             "productive discussion.\n\n"
        self.patient = self._update_system_message(self.patient, patient_env_prompt + self.general_prompt)

        # set simulator
        agents = [self.primary_doctor, self.patient]
        dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
        self._run_dial(dial_simulator)

        # _determine_consultation(self):
        consulation_decision = self.primary_doctor.model([
            SystemMessage(
                content='Here is the conversation history. Conclude the conversation and decide whether to call a consulation. Reply only with "Yes" or "No".'),
            HumanMessage(content=''.join(self.primary_doctor.message_history))
        ]).content
        if False and 'Yes' in consulation_decision:
        # if True:
            print('='*20 + 'BEGIN CONSULATION' + '='*20)
            doctors_index = self.primary_doctor.model([
                SystemMessage(
                    content=f'Here is the conversation history. Conclude the conversation and now, as the primary '
                            f'physician, your next step is to determine which specialty departments you need to invite '
                            f'for consultation. Please choose from the available [List of Candidate Specialties] and '
                            f'specify which departments you believe are essential for this case. Return your selection as '
                            f'a Python list containing the numerical indices of the chosen departments, without including '
                            f'the department names. For example, if you choose Cardiology and Neurology, '
                            f'your response should be: "[1, 2]" instead of "[1] Cardiology; [2] Neurology"; if you choose Gastroenterology, '
                            f'your response should be: "[5]" instead of "[5] Gastroenterology".\n\n[List of Candidate Specialties]: {self.departments}\n\n'
                            f'You MUST only reply with the list and do not say anything else!!!\n'
                            ),
                HumanMessage(content=''.join(self.primary_doctor.message_history))
            ]).content
            # doctors_index = '[5]'
            consulation_doctors = [self.departments_and_doctors_lst[i - 1] for i in eval(doctors_index)]
            diagnosis_report, precriptions = self.expert_consultation(consulation_doctors,
                                                                      (primary_doctor_name, primary_doctor_field), self.primary_doctor.message_history)
        else:
            print('=' * 20 + 'BEGIN INDEPENDENT DIAGNOSE' + '=' * 20)
            self.primary_doctor.reset_prompt()
            primary_doctor_env_prompt = f"You have already had an initial conversation with the patient, and " \
                                        f"[Chat History] is the record of your conversation. You will continue to be assuming the role of the primary " \
                                        f"physician for the patient. Your primary task is to inquire about the " \
                                        f"patient's medical condition and symptoms. As the primary physician, " \
                                        f"you will also be responsible for providing the final diagnosis and " \
                                        f"prescription based on the information provided by the patient. Your role is " \
                                        f"crucial in ensuring the patient receives the most appropriate care.\n\n [Chat History]: {self.primary_doctor.message_history}\n\n"
            self.primary_doctor = self._update_system_message(self.primary_doctor,
                                                              primary_doctor_env_prompt + self.general_prompt)
            # set simulator
            agents = [self.primary_doctor, self.patient]
            dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
            self._run_dial(dial_simulator)
            diagnosis_report, precriptions = self._generate_diagnosis_and_prescriptions(self.primary_doctor)
        return diagnosis_report, precriptions

    def expert_consultation(self, consulation_doctors, primary_doctor_info, chat_history):
        # reset prompt
        self.patient.reset_prompt()
        # set consulate doctors:
        agents = []
        for doctor_field, doctor_name in consulation_doctors:
            agents.append(self.set_doctor(doctor_name, doctor_field))

        # env prompt setting
        consulation_env_prompt = """
        [Consultation Environment Description]

        You are now in the consultation environment of SimuMed Virtual Hospital. In this consultation, the attending physician will lead the process, and both specialist doctors and the patient will actively participate in discussing the patient's condition to establish a diagnosis and prescription. The goal of the consultation is to create a unified and mutually accepted diagnosis for the patient and develop a corresponding treatment plan.

        [Consultation Process]

        1. Introduction by the Attending Physician: The primary physician will begin by introducing the patient's condition, symptoms, and medical history. Please listen attentively and prepare to contribute.

        2. Specialist Doctors' Input: Following this, specialist doctors will have the opportunity to speak one by one. Please provide analysis and recommendations regarding the patient's condition based on your specialized area.

        3. Patient's Input: The patient will also have the chance to express their observations, concerns, and questions regarding their condition. Please address the patient's input and questions as appropriate.

        4. Consensus Diagnosis: After the specialist doctors' and patient's discussions, the primary physician will summarize the results to reach a unanimous diagnosis. Please actively participate in the diagnosis formulation.

        5. Prescription Development: Based on the diagnosis, the doctors will collaboratively create a prescription, including medications.py and treatment measures. The prescription requires approval from all doctors.

        [Conclusion of the Consultation]

        Following the consultation, the primary physician will draft a diagnosis report and prescription to ensure accuracy and comprehensiveness. Subsequently, the consultation results will be shared with the patient to create a follow-up treatment plan.

        Please actively engage in the consultation discussion according to your specialized area or as the patient to ensure the patient receives the best medical advice and treatment plan. Thank you for your cooperation and professionalism.\n\n
        """
        for i in range(len(agents)):
            agents[i] = self._update_system_message(agents[i], consulation_env_prompt + self.general_prompt)

        # 病人
        patient_env_prompt = f"In the following conversation, you will attend the consultation and your primary task is to describe your symptoms and " \
                             f"answer any questions that the doctors may ask. Please be cooperative and provide clear " \
                             f"information about your condition. If you have any questions or need clarification, " \
                             f"feel free to ask the doctors for assistance. Your active participation is essential for a " \
                             f"productive discussion. You have talked with the primary doctor, and the conversation history is:\n\n{chat_history}\n\n"
        self.patient = self._update_system_message(self.patient, patient_env_prompt + self.general_prompt)

        agents.append(self.patient)

        # 主治医生
        primary_doctor = self.set_director_primary_doctor(*primary_doctor_info, agents)
        primary_doctor_env_prompt = f"As the primary physician, you lead this consultation, " \
                                    f"guiding discussions, summarizing diagnoses, " \
                                    f"and ensuring consensus among specialists. Engage the " \
                                    f"patient and facilitate unified decisions on diagnosis " \
                                    f"and treatment. You have had an initial conversation with the patient, " \
                                    f"gathered some information, and the conversation transcript is saved in the [Chat History]." \
                                    f"Thank you for your vital role.\n\n[Chat History]: {chat_history}\n\n"
        primary_doctor = self._update_system_message(primary_doctor, consulation_env_prompt + primary_doctor_env_prompt + self.general_prompt)

        # 对话
        agents.insert(0, primary_doctor)
        dial_simulator = self._set_dial_simulator(agents=agents,
                                                  speaker_select_func=functools.partial(self._speak_with_directed,
                                                                                        director=primary_doctor))
        self._run_dial(dial_simulator)
        diagnosis_report, precriptions = self._generate_diagnosis_and_prescriptions(primary_doctor)
        return diagnosis_report, precriptions

    def _generate_diagnosis_and_prescriptions(self, primary_doctor):
        diagnosis_report = primary_doctor.model([
            SystemMessage(
                content='Here is the conversation history. Conclude the conversation and generate the diagnosis report of the patient. Let\'s think step by step.'),
            HumanMessage(content=''.join(primary_doctor.message_history))
        ]).content
        precriptions = primary_doctor.model([
            SystemMessage(
                content='Here is the conversation history. Conclude the conversation and generate the precriptions for the patient. Let\'s think step by step.'),
            HumanMessage(content=''.join(primary_doctor.message_history))
        ]).content
        return diagnosis_report, precriptions

    def collaborative_prescription(self, diagnosis_report, precriptions):
        # reset_prompt
        self.primary_doctor.reset_prompt()
        # set env prompt
        pharmacist_env_prompt = "In your role as a pharmacist, your primary responsibility is to review and verify " \
                                "prescriptions provided by the primary physician. Your focus is on ensuring the " \
                                "safety and effectiveness of the prescribed medications.py. If you identify any issues " \
                                "or potential risks with the prescription, please provide feedback to the primary " \
                                "physician for necessary modifications. Collaborate with the physician until you are " \
                                "confident that the prescription is safe and appropriate for the patient.\n\n"
        primary_doctor_env_prompt = f"As the primary physician, your role includes submitting the [Diagnosis Report] and " \
                                    f"[Prescription] to the pharmacist for review. The pharmacist will carefully assess " \
                                    f"the prescription based on the provided diagnosis report to ensure safety and " \
                                    f"effectiveness. If the pharmacist provides feedback or identifies any issues with " \
                                    f"the prescription, kindly address those concerns and make necessary " \
                                    f"modifications. Continue this collaborative process with the pharmacist until the " \
                                    f"prescription is deemed safe and suitable for the patient. \n\n" \
                                    f"[Diagnosis Report]:\n\n{diagnosis_report}\n\n[Prescription]:\n\n{precriptions}\n\n"
        self.pharmacist = self._update_system_message(self.pharmacist, pharmacist_env_prompt + self.general_prompt)
        self.primary_doctor = self._update_system_message(self.primary_doctor, primary_doctor_env_prompt + self.general_prompt)

        agents = [self.pharmacist, self.primary_doctor]
        dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
        self._run_dial(dial_simulator)
        detailed_prescriptions = self.pharmacist.model([
            SystemMessage(
                content='Here is the conversation history. Conclude the conversation and generate the detailed '
                        'prescriptions. The detailed prescriptions should include the usage notations and '
                        'explanations.'),
            HumanMessage(content=''.join(self.pharmacist.message_history))
        ]).content
        return detailed_prescriptions

    def prescription_communication(self, detailed_prescriptions):
        # reset prompt
        self.patient.reset_prompt()
        self.pharmacist.reset_prompt()
        # env prompt
        pharmacist_env_prompt = f"As the pharmacist, your next step is to engage in a conversation with the patient. " \
                                f"Present the [Prescription] to the patient, address any questions or concerns they " \
                                f"may have, and provide guidance on how to properly use the prescribed medications.py or " \
                                f"follow the recommended medical procedures. [Prescription]: {detailed_prescriptions}\n\n"
        patient_env_prompt = "In the upcoming conversation, you will be interacting with the pharmacist. Your task is " \
                             "to review the prescription provided by the pharmacist and inquire about any aspects " \
                             "that are unclear or raise questions. Feel free to ask for clarification or express any " \
                             "concerns you may have regarding the prescribed medications.py or medical procedures.\n\n"
        self.pharmacist = self._update_system_message(self.pharmacist, pharmacist_env_prompt + self.general_prompt)
        self.patient = self._update_system_message(self.patient, patient_env_prompt + self.general_prompt)

        agents = [self.pharmacist, self.patient]
        dial_simulator = self._set_dial_simulator(agents=agents, speaker_select_func=self._speak_in_turn)
        self._run_dial(dial_simulator)
        return

    def simulate(self):
        primary_doctor_name, primary_doctor_field = self.nurse_triage_patient()
        # primary_doctor_name, primary_doctor_field = "Pediatrician", "Pediatrics"
        diagnosis_report, precriptions = self.doctor_treat_patient(primary_doctor_name, primary_doctor_field)
        detailed_prescription = self.collaborative_prescription(diagnosis_report, precriptions)
        self.prescription_communication(detailed_prescription)

def main():
    patient_statement = 'My baby has been pooing 5-6 times a day for a week. In the last few days it has increased to ' \
                        '7 and they are very watery with green stringy bits in them. He does not seem unwell i.e no ' \
                        'temperature and still eating. He now has a very bad nappy rash from the pooing ...help! '
    simumed = SimuHospital(ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2, max_retries=100), patient_statement=patient_statement)
    simumed.simulate()


if __name__ == '__main__':
    main()
