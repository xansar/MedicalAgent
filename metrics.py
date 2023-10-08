# -*- coding: utf-8 -*-

"""
@author: xansar
@software: PyCharm
@file: metrics.py
@time: 2023/9/26 11:23
@e-mail: xansar@ruc.edu.cn
"""

class Metrics:
    def __init__(self, ddi_matrix, med_map):
        self.ddi_matrix = ddi_matrix
        self.med_map = med_map

    @staticmethod
    def jaccard(pred, label):
        # 计算交集的大小
        intersection = len(set(pred).intersection(label))

        # 计算并集的大小
        union = len(set(pred).union(label))

        # 计算Jaccard相似度
        jaccard_similarity = intersection / union
        return jaccard_similarity

    @staticmethod
    def PRF1(pred, label):
        # 计算True Positives（真正）、False Positives（假正）、False Negatives（假负）
        tp = len(set(label).intersection(pred))
        fp = len(set(pred) - set(label))
        fn = len(set(label) - set(pred))
        if tp == 0.:
            return 0., 0., 0.
        # 计算Precision（精确率）和Recall（召回率）
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        # 计算F1-score
        f1_score = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1_score

    def ddi_rate(self, drug_list):
        interaction_count = 0
        total_pair_count = 0
        for i in range(len(drug_list)):
            for j in range(i + 1, len(drug_list)):  # 避免计算自身与自身的相互作用
                drug_i = drug_list[i]
                drug_j = drug_list[j]

                # 检查邻接矩阵中是否存在相互作用
                if self.ddi_matrix[drug_i][drug_j] == 1:
                    interaction_count += 1

                total_pair_count += 1

        # 计算相互作用率（ddi_rate）
        ddi_rate = interaction_count / total_pair_count
        return ddi_rate

    def compute(self, pred, label):
        # transfer codes to idx
        pred_idx = [self.med_map['med2idx'][med] for med in pred]
        label_idx = [self.med_map['med2idx'][med] for med in label]

        jaccard = self.jaccard(pred_idx, label_idx)
        if len(pred) == 0:
            precision, recall, f1_score = 0., 0., 0.
            ddi_rate = 0.
        else:
            precision, recall, f1_score = self.PRF1(pred_idx, label_idx)
            ddi_rate = self.ddi_rate(pred_idx)
        length = len(pred_idx)

        metrics_dict = {
            'Jaccard': jaccard,
            'Precision': precision,
            'Recall': recall,
            'F1 Score': f1_score,
            'DDI Rate': ddi_rate,
            'Length': length
        }

        return metrics_dict