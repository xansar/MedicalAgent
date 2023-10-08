drug_lst = """
            1. R05D - Expectorants, excluding combinations with cough suppressants
            2. P01B - Antimalarials, other agents
            3. A12B - Vitamins, other combinations
            4. N03A - Antiepileptics
            5. A07E - Intestinal adsorbents
            6. D10A - Anti-acne preparations for topical use
            7. H03A - Thyroid preparations
            8. N02B - Other analgesics and antipyretics
            9. B01A - Antithrombotic agents
            10. A06A - Drugs for constipation
            11. A02B - Drugs for peptic ulcer and gastro-oesophageal reflux disease (GORD)
            12. D01A - Antifungals for dermatological use
            13. D06B - Antibiotics and chemotherapeutics for dermatological use
            14. A07A - Antidiarrheal microorganisms
            15. B05C - Electrolyte solutions
            16. J05A - Direct-acting antivirals
            17. A12C - Calcium, combinations with vitamin D and/or other drugs
            18. A07D - Antipropulsives
            19. L04A - Immunosuppressants
            20. C07A - Beta-blocking agents
            21. C08C - Selective calcium channel blockers with mainly vascular effects
            22. D11A - Other dermatological preparations
            23. C03C - Potassium-sparing agents
            24. R03A - Adrenergics in combination with corticosteroids or other drugs, excl. anticholinergics
            25. A12A - Calcium
            26. A03F - Propulsives
            27. N02A - Opioids
            28. D04A - Antipruritics, including antihistamines, anesthetics, etc.
            29. J01E - Sulfonamides, plain
            30. J01C - Beta-lactam antibacterials, penicillins
            31. D06A - Corticosteroids, plain
            32. J01M - Quinolone antibacterials
            33. A01A - Stomatological preparations
            34. C02D - Dihydropyridine derivatives
            35. C01C - Cardiac stimulants excluding cardiac glycosides
            36. N01A - Anesthetics
            37. A04A - Antiemetics and antinauseants
            38. N05A - Antipsychotics
            39. N06A - Antidepressants
            40. L01A - Alkylating agents
            41. B02B - Other antihemorrhagics
            42. N05B - Anxiolytics
            43. C02A - Antiadrenergic agents, centrally acting
            44. C05A - Agents for treatment of hemorrhoids and anal fissures for topical use
            45. R01A - Nasal decongestants for systemic use
            46. C10A - Lipid modifying agents, plain
            47. C09A - Ace inhibitors and calcium channel blockers
            48. N05C - Hypnotics and sedatives
            49. M01A - Anti-inflammatory and antirheumatic products, non-steroids
            50. N07A - Parasympathomimetics
            51. A02A - Antacids
            52. A10B - Blood glucose lowering drugs, excl. insulins
            53. C01E - Other cardiac preparations
            54. B03B - Antianemic preparations
            55. C09C - Angiotensin II antagonists, plain
            56. A11C - Vitamins, plain
            57. C03A - High-ceiling diuretics
            58. A03B - Belladonna and derivatives, plain
            59. C01B - Antiarrhythmics, class I and III
            60. J01D - Other beta-lactam antibacterials
            61. R06A - Antihistamines for systemic use
            62. J01X - Other antibacterials
            63. C03D - Aldosterone antagonists
            64. C01A - Cardiac glycosides
            65. C01D - Vasodilators used in cardiac diseases
            66. G04C - Drugs for urinary frequency and incontinence
            67. D07A - Corticosteroids, dermatological preparations
            68. S01E - Antiinfectives
            69. M03A - Muscle relaxants, centrally acting agents
            70. N07B - Other drugs used in addictive disorders
            71. R05C - Cough suppressants, excl. combinations with expectorants
            72. G04B - Urologicals
            73. C02C - Antiadrenergic agents, non-selective
            74. C05B - Sclerosing agents for local injection
            75. N01B - Anesthetics, local
            76. M04A - Antigout preparations
            77. A11D - Vitamins, combinations with other vitamins
            78. H01C - Corticosteroids for systemic use, plain
            79. A05A - Bile and liver therapy
            80. P01C - Antiprotozoals
            81. L01B - Antimetabolites
            82. H02A - Glucocorticoids
            83. P01A - Agents against amoebiasis and other protozoal diseases
            84. J02A - Antimycotics for systemic use
            85. L01X - Other antineoplastic agents
            86. J01F - Other antibacterials for systemic use
            87. G02C - Other gynecologicals
            88. V03A - All other therapeutic products
            89. G03A - Hormonal contraceptives for systemic use
            90. J04A - Drugs for treatment of tuberculosis
            91. N04B - Dopaminergic agents
            92. N06B - Psychostimulants, agents used for ADHD and nootropics
            93. H05B - Antithyroid agents
            94. J01G - Aminoglycosides
            95. C08D - Selective calcium channel blockers with direct cardiac effects
            96. N06D - Antidementia drugs
            97. S01F - Mydriatics and cycloplegics
            98. M03B - Other centrally acting agents and muscle relaxants
            99. M05B - Drugs affecting bone structure and mineralization
            100. H03B - Thyroid preparations
            101. B02A - Antihemorrhagics
            102. D08A - Antiseptics and disinfectants
            103. A16A - Other alimentary tract and metabolism products
            104. J01A - Antibacterials for systemic use
            105. A11G - Vitamin B-complex, other combinations
            106. P02C - Antinematodal agents
            107. L01D - Cytotoxic antibiotics and related substances
            108. C03B - Sulfonamides, plain
            109. A03A - Bile preparations
            110. G03C - Estrogens
            111. N04A - Anticholinergic agents
            112. N02C - Antimigraine preparations
            113. A07B - Intestinal antiinflammatory agents
            114. M02A - Topical products for joint and muscular pain
            115. D05A - Antipsoriatics
            116. A11H - Other plain vitamin preparations
            117. R01B - Nasal preparations
            118. S01H - Otologicals
            119. A09A - Digestives, incl. enzymes
            120. L02B - Hormone antagonists and related agents
            121. L01C - Plant alkaloids and derivatives
            122. H01B - Antithyroid agents
            123. G01A - Antimycotics and antibiotics, see D01 and J02
            124. J06B - Vaccines
            125. C03X - Other diuretics
            126. G03B - Hormonal contraceptives for systemic use, progestogens only
            127. S01K - Ophthalmologicals
            128. M01C - Anti-inflammatory and antirheumatic products, steroids
            129. V04C - Other diagnostic agents
            130. R02A - Throat preparations
            131. S01A - Antiinfectives
            """