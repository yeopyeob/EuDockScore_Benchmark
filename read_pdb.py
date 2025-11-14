import json
import numpy as np
from pathlib import Path
from typing import Union
from dataclasses import dataclass, field

#
# Criteria : Heavy Atom Distance
d_min_contact = 5
#
atom_types = [
    "NONE",
    "N",
    "CA",
    "C",
    "CB",
    "O",
    "CG",
    "CG1",
    "CG2",
    "OG",
    "OG1",
    "SG",
    "CD",
    "CD1",
    "CD2",
    "ND1",
    "ND2",
    "OD1",
    "OD2",
    "SD",
    "CE",
    "CE1",
    "CE2",
    "CE3",
    "NE",
    "NE1",
    "NE2",
    "OE1",
    "OE2",
    "CH2",
    "NH1",
    "NH2",
    "OH",
    "CZ",
    "CZ2",
    "CZ3",
    "NZ",  # , 'OXT'
]
CA_IDX = atom_types.index("CA")
CB_IDX = atom_types.index("CB")
#
STANDARD = "UNK ALA GLY ILE LEU PRO VAL PHE TRP TYR ASP GLU ARG HIS LYS SER THR CYS MET ASN GLN".split()
STANDARD_inv = {
    "UNK": "X",
    "ALA": "A",
    "GLY": "G",
    "ILE": "I",
    "LEU": "L",
    "PRO": "P",
    "VAL": "V",
    "PHE": "F",
    "TRP": "W",
    "TYR": "Y",
    "ASP": "D",
    "GLU": "E",
    "ARG": "R",
    "HIS": "H",
    "LYS": "K",
    "SER": "S",
    "THR": "T",
    "CYS": "C",
    "MET": "M",
    "ASN": "N",
    "GLN": "Q",
}
STANDARD_ID = {k: i for i, k in enumerate(list(STANDARD_inv.keys()))}
GLY_IDX = STANDARD_ID["GLY"]
STANDARD_ID["UNK"] = 0
STANDARD_ID_ONE_LETTER = {STANDARD_inv[k]: v for k, v in STANDARD_ID.items()}
#
# + charge : 0, - charge : 1, polar : 2, nonpolar : 3, unknown : 4
classification = {
    "ALA": 3,
    "GLY": 3,
    "ILE": 3,
    "LEU": 3,
    "PRO": 3,
    "VAL": 3,
    "PHE": 3,
    "TRP": 3,
    "TYR": 3,
    "ASP": 1,
    "GLU": 1,
    "ARG": 0,
    "HIS": 0,
    "LYS": 0,
    "SER": 2,
    "THR": 2,
    "CYS": 3,
    "MET": 3,
    "ASN": 2,
    "GLN": 2,
    "UNK": 4,
}
#
classification_inv = {
    0: ["R", "H", "L"],
    1: ["D", "E"],
    2: ["S", "T", "N", "Q"],
    3: ["A", "G", "I", "L", "P", "V", "F", "W", "Y", "C", "M"],
    4: ["X"],
}
#
# hbond_atom = [[donor], [acceptor]]
hbond_atom = {
    "ARG": [["N", "O", "NE", "NH1", "NH2"], ["N", "O"]],
    "HIS": [["N", "O", "ND1", "NE2"], ["N", "O", "ND1", "NE2"]],
    "LYS": [["N", "O", "NZ"], ["N", "O"]],
    "ASP": [["N", "O"], ["N", "O", "OD1", "OD2"]],
    "GLU": [["N", "O"], ["N", "O", "OE1", "OE2"]],
    "SER": [["N", "O", "OG"], ["N", "O", "OG"]],
    "THR": [["N", "O", "OG1"], ["N", "O", "OG1"]],
    "ASN": [["N", "O", "ND2"], ["N", "O", "OD1"]],
    "GLN": [["N", "O", "NE2"], ["N", "O", "OE1"]],
    "CYS": [["N", "O"], ["N", "O"]],
    "GLY": [["N", "O"], ["N", "O"]],
    "PRO": [["N", "O"], ["N", "O"]],
    "ALA": [["N", "O"], ["N", "O"]],
    "VAL": [["N", "O"], ["N", "O"]],
    "LEU": [["N", "O"], ["N", "O"]],
    "ILE": [["N", "O"], ["N", "O"]],
    "MET": [["N", "O"], ["N", "O"]],
    "PHE": [["N", "O"], ["N", "O"]],
    "TYR": [["N", "O", "OH"], ["N", "O", "OH"]],
    "TRP": [["N", "O", "NE1"], ["N", "O"]],
}
#
hydrophobic_residues = ["ALA", "VAL", "LEU", "ILE", "MET", "PHE", "TRP", "PRO", "TYR"]
positive_residues = ["ARG", "LYS", "HIS"]
negative_residues = ["ASP", "GLU"]
polar_residues = ["SER", "THR", "ASN", "GLN", "CYS"]
ionic_residues = positive_residues + negative_residues
#
restype_name_to_atom14_names = {
    "ALA": ["N", "CA", "C", "O", "CB", "", "", "", "", "", "", "", "", ""],
    "ARG": [
        "N",
        "CA",
        "C",
        "O",
        "CB",
        "CG",
        "CD",
        "NE",
        "CZ",
        "NH1",
        "NH2",
        "",
        "",
        "",
    ],
    "ASN": ["N", "CA", "C", "O", "CB", "CG", "OD1", "ND2", "", "", "", "", "", ""],
    "ASP": ["N", "CA", "C", "O", "CB", "CG", "OD1", "OD2", "", "", "", "", "", ""],
    "CYS": ["N", "CA", "C", "O", "CB", "SG", "", "", "", "", "", "", "", ""],
    "GLN": ["N", "CA", "C", "O", "CB", "CG", "CD", "OE1", "NE2", "", "", "", "", ""],
    "GLU": ["N", "CA", "C", "O", "CB", "CG", "CD", "OE1", "OE2", "", "", "", "", ""],
    "GLY": ["N", "CA", "C", "O", "", "", "", "", "", "", "", "", "", ""],
    "HIS": [
        "N",
        "CA",
        "C",
        "O",
        "CB",
        "CG",
        "ND1",
        "CD2",
        "CE1",
        "NE2",
        "",
        "",
        "",
        "",
    ],
    "ILE": ["N", "CA", "C", "O", "CB", "CG1", "CG2", "CD1", "", "", "", "", "", ""],
    "LEU": ["N", "CA", "C", "O", "CB", "CG", "CD1", "CD2", "", "", "", "", "", ""],
    "LYS": ["N", "CA", "C", "O", "CB", "CG", "CD", "CE", "NZ", "", "", "", "", ""],
    "MET": ["N", "CA", "C", "O", "CB", "CG", "SD", "CE", "", "", "", "", "", ""],
    "PHE": [
        "N",
        "CA",
        "C",
        "O",
        "CB",
        "CG",
        "CD1",
        "CD2",
        "CE1",
        "CE2",
        "CZ",
        "",
        "",
        "",
    ],
    "PRO": ["N", "CA", "C", "O", "CB", "CG", "CD", "", "", "", "", "", "", ""],
    "SER": ["N", "CA", "C", "O", "CB", "OG", "", "", "", "", "", "", "", ""],
    "THR": ["N", "CA", "C", "O", "CB", "OG1", "CG2", "", "", "", "", "", "", ""],
    "TRP": [
        "N",
        "CA",
        "C",
        "O",
        "CB",
        "CG",
        "CD1",
        "CD2",
        "NE1",
        "CE2",
        "CE3",
        "CZ2",
        "CZ3",
        "CH2",
    ],
    "TYR": [
        "N",
        "CA",
        "C",
        "O",
        "CB",
        "CG",
        "CD1",
        "CD2",
        "CE1",
        "CE2",
        "CZ",
        "OH",
        "",
        "",
    ],
    "VAL": ["N", "CA", "C", "O", "CB", "CG1", "CG2", "", "", "", "", "", "", ""],
    "UNK": ["", "", "", "", "", "", "", "", "", "", "", "", "", ""],
}
#
modres = {
    "0CS": "ALA",  # 0CS ALA  3-[(S)-HYDROPEROXYSULFINYL]-L-ALANINE
    "0AF": "TRP",
    "1AB": "PRO",  # 1AB PRO  1,4-DIDEOXY-1,4-IMINO-D-ARABINITOL
    "1LU": "LEU",  # 1LU LEU  4-METHYL-PENTANOIC ACID-2-OXYL GROUP
    "1PA": "PHE",  # 1PA PHE  PHENYLMETHYLACETIC ACID ALANINE
    "1TQ": "TRP",  # 1TQ TRP  6-(FORMYLAMINO)-7-HYDROXY-L-TRYPTOPHAN
    "1TY": "TYR",  # 1TY TYR
    "23F": "PHE",  # 23F PHE  (2Z)-2-AMINO-3-PHENYLACRYLIC ACID
    "23S": "TRP",  # 23S TRP  MODIFIED TRYPTOPHAN
    "2BU": "ALA",  # 2BU ADE
    "2HF": "HIS",  # 2HF HIS  2-FLUOROHISTIDINE
    "2ML": "LEU",  # 2ML LEU  2-METHYLLEUCINE
    "2MR": "ARG",  # 2MR ARG  N3, N4-DIMETHYLARGININE
    "2MT": "PRO",  # 2MT PRO
    "2OP": "ALA",  # 2OP (2S  2-HYDROXYPROPANAL
    "2TY": "TYR",  # 2TY TYR
    "32S": "TRP",  # 32S TRP  MODIFIED TRYPTOPHAN
    "32T": "TRP",  # 32T TRP  MODIFIED TRYPTOPHAN
    "3AH": "HIS",  # 3AH HIS
    "3MD": "ASP",  # 3MD ASP  2S,3S-3-METHYLASPARTIC ACID
    "3TY": "TYR",  # 3TY TYR  MODIFIED TYROSINE
    "4DP": "TRP",  # 4DP TRP
    "4F3": "ALA",  # 4F3 ALA  CYCLIZED
    "4FB": "PRO",  # 4FB PRO  (4S)-4-FLUORO-L-PROLINE
    "4FW": "TRP",  # 4FW TRP  4-FLUOROTRYPTOPHANE
    "4HT": "TRP",  # 4HT TRP  4-HYDROXYTRYPTOPHAN
    "4IN": "TRP",  # 4IN TRP  4-AMINO-L-TRYPTOPHAN
    "4PH": "PHE",  # 4PH PHE  4-METHYL-L-PHENYLALANINE
    "5CS": "CYS",  # 5CS CYS
    "6CL": "LYS",  # 6CL LYS  6-CARBOXYLYSINE
    "6CW": "TRP",  # 6CW TRP  6-CHLORO-L-TRYPTOPHAN
    "A0A": "ASP",  # A0A ASP  ASPARTYL-FORMYL MIXED ANHYDRIDE
    "AA4": "ALA",  # AA4 ALA  2-AMINO-5-HYDROXYPENTANOIC ACID
    "AAR": "ARG",  # AAR ARG  ARGININEAMIDE
    "AB7": "GLU",  # AB7 GLU  ALPHA-AMINOBUTYRIC ACID
    "ABA": "ALA",  # ABA ALA  ALPHA-AMINOBUTYRIC ACID
    "ACB": "ASP",  # ACB ASP  3-METHYL-ASPARTIC ACID
    "ACL": "ARG",  # ACL ARG  DEOXY-CHLOROMETHYL-ARGININE
    "ACY": "GLY",  # ACY GLY  POST-TRANSLATIONAL MODIFICATION
    "AEI": "THR",  # AEI THR  ACYLATED THR
    "AFA": "ASN",  # AFA ASN  N-[7-METHYL-OCT-2,4-DIENOYL]ASPARAGINE
    "AGM": "ARG",  # AGM ARG  4-METHYL-ARGININE
    "AGT": "CYS",  # AGT CYS  AGMATINE-CYSTEINE ADDUCT
    "AHB": "ASN",  # AHB ASN  BETA-HYDROXYASPARAGINE
    "AHO": "ALA",  # AHO ALA  N-ACETYL-N-HYDROXY-L-ORNITHINE
    "AHP": "ALA",  # AHP ALA  2-AMINO-HEPTANOIC ACID
    "AIB": "ALA",  # AIB ALA  ALPHA-AMINOISOBUTYRIC ACID
    "AKL": "ASP",  # AKL ASP  3-AMINO-5-CHLORO-4-OXOPENTANOIC ACID
    "ALA": "ALA",  # ALA ALA
    "ALB": "ALA",  # ALB ALA
    "ALC": "ALA",  # ALC ALA  2-AMINO-3-CYCLOHEXYL-PROPIONIC ACID
    "ALG": "ARG",  # ALG ARG  GUANIDINOBUTYRYL GROUP
    "ALM": "ALA",  # ALM ALA  1-METHYL-ALANINAL
    "ALN": "ALA",  # ALN ALA  NAPHTHALEN-2-YL-3-ALANINE
    "ALO": "THR",  # ALO THR  ALLO-THREONINE
    "ALS": "ALA",  # ALS ALA  2-AMINO-3-OXO-4-SULFO-BUTYRIC ACID
    "ALT": "ALA",  # ALT ALA  THIOALANINE
    "ALY": "LYS",  # ALY LYS  N(6)-ACETYLLYSINE
    "AME": "MET",  # AME MET  ACETYLATED METHIONINE
    "AP7": "ALA",  # AP7 ADE
    "APH": "ALA",  # APH ALA  P-AMIDINOPHENYL-3-ALANINE
    "API": "LYS",  # API LYS  2,6-DIAMINOPIMELIC ACID
    "APK": "LYS",  # APK LYS
    "AR2": "ARG",  # AR2 ARG  ARGINYL-BENZOTHIAZOLE-6-CARBOXYLIC ACID
    "AR4": "GLU",  # AR4 GLU
    "ARG": "ARG",  # ARG ARG
    "ARM": "ARG",  # ARM ARG  DEOXY-METHYL-ARGININE
    "ARO": "ARG",  # ARO ARG  C-GAMMA-HYDROXY ARGININE
    "ASA": "ASP",  # ASA ASP  ASPARTIC ALDEHYDE
    "ASB": "ASP",  # ASB ASP  ASPARTIC ACID-4-CARBOXYETHYL ESTER
    "ASH": "ASP",  # ASH ASP
    "ASI": "ASP",  # ASI ASP  L-ISO-ASPARTATE
    "ASK": "ASP",  # ASK ASP  DEHYDROXYMETHYLASPARTIC ACID
    "ASL": "ASP",  # ASL ASP  ASPARTIC ACID-4-CARBOXYETHYL ESTER
    "ASQ": "ASP",  # ASQ ASP
    "ASM": "ASN",  # ASM ASN
    "ASN": "ASN",  # ASN ASN
    "ASZ": "ASN",  # ASZ ASN
    "ASP": "ASP",  # ASP ASP
    "AYA": "ALA",  # AYA ALA  N-ACETYLALANINE
    "AYG": "ALA",  # AYG ALA
    "AZK": "LYS",  # AZK LYS  (2S)-2-AMINO-6-TRIAZANYLHEXAN-1-OL
    "B2A": "ALA",  # B2A ALA  ALANINE BORONIC ACID
    "B2F": "PHE",  # B2F PHE  PHENYLALANINE BORONIC ACID
    "B2I": "ILE",  # B2I ILE  ISOLEUCINE BORONIC ACID
    "B2V": "VAL",  # B2V VAL  VALINE BORONIC ACID
    "B3A": "ALA",  # B3A ALA  (3S)-3-AMINOBUTANOIC ACID
    "B3D": "ASP",  # B3D ASP  3-AMINOPENTANEDIOIC ACID
    "B3E": "GLU",  # B3E GLU  (3S)-3-AMINOHEXANEDIOIC ACID
    "B3K": "LYS",  # B3K LYS  (3S)-3,7-DIAMINOHEPTANOIC ACID
    "B3S": "SER",  # B3S SER  (3R)-3-AMINO-4-HYDROXYBUTANOIC ACID
    "B3X": "ASN",  # B3X ASN  (3S)-3,5-DIAMINO-5-OXOPENTANOIC ACID
    "B3Y": "TYR",  # B3Y TYR
    "BAL": "ALA",  # BAL ALA  BETA-ALANINE
    "BBC": "CYS",  # BBC CYS
    "BCS": "CYS",  # BCS CYS  BENZYLCYSTEINE
    "BCX": "CYS",  # BCX CYS  BETA-3-CYSTEINE
    "BFD": "ASP",  # BFD ASP  ASPARTATE BERYLLIUM FLUORIDE
    "BG1": "SER",  # BG1 SER
    "BHD": "ASP",  # BHD ASP  BETA-HYDROXYASPARTIC ACID
    "BIF": "PHE",  # BIF PHE
    "BLE": "LEU",  # BLE LEU  LEUCINE BORONIC ACID
    "BLY": "LYS",  # BLY LYS  LYSINE BORONIC ACID
    "BMT": "THR",  # BMT THR
    "BNN": "ALA",  # BNN ALA  ACETYL-P-AMIDINOPHENYLALANINE
    "BOR": "ARG",  # BOR ARG
    "BPE": "CYS",  # BPE CYS
    "BTR": "TRP",  # BTR TRP  6-BROMO-TRYPTOPHAN
    "BUC": "CYS",  # BUC CYS  S,S-BUTYLTHIOCYSTEINE
    "BUG": "LEU",  # BUG LEU  TERT-LEUCYL AMINE
    "C12": "ALA",  # C12 ALA
    "C1X": "LYS",  # C1X LYS  MODIFIED LYSINE
    "C3Y": "CYS",  # C3Y CYS  MODIFIED CYSTEINE
    "C5C": "CYS",  # C5C CYS  S-CYCLOPENTYL THIOCYSTEINE
    "C6C": "CYS",  # C6C CYS  S-CYCLOHEXYL THIOCYSTEINE
    "C99": "ALA",  # C99 ALA
    "CAB": "ALA",  # CAB ALA  4-CARBOXY-4-AMINOBUTANAL
    "CAF": "CYS",  # CAF CYS  S-DIMETHYLARSINOYL-CYSTEINE
    "CAS": "CYS",  # CAS CYS  S-(DIMETHYLARSENIC)CYSTEINE
    "CCS": "CYS",  # CCS CYS  CARBOXYMETHYLATED CYSTEINE
    "CGU": "GLU",  # CGU GLU  CARBOXYLATION OF THE CG ATOM
    "CH6": "ALA",  # CH6 ALA
    "CH7": "ALA",  # CH7 ALA
    "CHG": "GLY",  # CHG GLY  CYCLOHEXYL GLYCINE
    "CHP": "GLY",  # CHP GLY  3-CHLORO-4-HYDROXYPHENYLGLYCINE
    "CHS": "PHE",  # CHS PHE  4-AMINO-5-CYCLOHEXYL-3-HYDROXY-PENTANOIC AC
    "CIR": "ARG",  # CIR ARG  CITRULLINE
    "CLB": "ALA",  # CLB ALA
    "CLD": "ALA",  # CLD ALA
    "CLE": "LEU",  # CLE LEU  LEUCINE AMIDE
    "CLG": "LYS",  # CLG LYS
    "CLH": "LYS",  # CLH LYS
    "CLV": "ALA",  # CLV ALA
    "CME": "CYS",  # CME CYS  MODIFIED CYSTEINE
    "CML": "CYS",  # CML CYS
    "CMT": "CYS",  # CMT CYS  O-METHYLCYSTEINE
    "CQR": "ALA",  # CQR ALA
    "CR2": "ALA",  # CR2 ALA  POST-TRANSLATIONAL MODIFICATION
    "CR5": "ALA",  # CR5 ALA
    "CR7": "ALA",  # CR7 ALA
    "CR8": "ALA",  # CR8 ALA
    "CRK": "ALA",  # CRK ALA
    "CRO": "THR",  # CRO THR  CYCLIZED
    "CRQ": "TYR",  # CRQ TYR
    "CRW": "ALA",  # CRW ALA
    "CRX": "ALA",  # CRX ALA
    "CS1": "CYS",  # CS1 CYS  S-(2-ANILINYL-SULFANYL)-CYSTEINE
    "CS3": "CYS",  # CS3 CYS
    "CS4": "CYS",  # CS4 CYS
    "CSA": "CYS",  # CSA CYS  S-ACETONYLCYSTEIN
    "CSB": "CYS",  # CSB CYS  CYS BOUND TO LEAD ION
    "CSD": "CYS",  # CSD CYS  3-SULFINOALANINE
    "CSE": "CYS",  # CSE CYS  SELENOCYSTEINE
    "CSI": "ALA",  # CSI ALA
    "CSO": "CYS",  # CSO CYS  INE S-HYDROXYCYSTEINE
    "CSR": "CYS",  # CSR CYS  S-ARSONOCYSTEINE
    "CSS": "CYS",  # CSS CYS  1,3-THIAZOLE-4-CARBOXYLIC ACID
    "CSU": "CYS",  # CSU CYS  CYSTEINE-S-SULFONIC ACID
    "CSW": "CYS",  # CSW CYS  CYSTEINE-S-DIOXIDE
    "CSX": "CYS",  # CSX CYS  OXOCYSTEINE
    "CSY": "ALA",  # CSY ALA  MODIFIED TYROSINE COMPLEX
    "CSZ": "CYS",  # CSZ CYS  S-SELANYL CYSTEINE
    "CTH": "THR",  # CTH THR  4-CHLOROTHREONINE
    "CWR": "ALA",  # CWR ALA
    "CXM": "MET",  # CXM MET  N-CARBOXYMETHIONINE
    "CY0": "CYS",  # CY0 CYS  MODIFIED CYSTEINE
    "CY1": "CYS",  # CY1 CYS  ACETAMIDOMETHYLCYSTEINE
    "CY3": "CYS",  # CY3 CYS  2-AMINO-3-MERCAPTO-PROPIONAMIDE
    "CY4": "CYS",  # CY4 CYS  S-BUTYRYL-CYSTEIN
    "CY7": "CYS",  # CY7 CYS  MODIFIED CYSTEINE
    "CYD": "CYS",  # CYD CYS
    "CYF": "CYS",  # CYF CYS  FLUORESCEIN LABELLED CYS380 (P14)
    "CYG": "CYS",  # CYG CYS
    "CYJ": "LYS",  # CYJ LYS  MODIFIED LYSINE
    "CYM": "CYS",  # CYM CYS
    "CYQ": "CYS",  # CYQ CYS
    "CYR": "CYS",  # CYR CYS
    "CYS": "CYS",  # CYS CYS
    "CYT": "CYS",  # CYT CYS
    "CZ2": "CYS",  # CZ2 CYS  S-(DIHYDROXYARSINO)CYSTEINE
    "CZZ": "CYS",  # CZZ CYS  THIARSAHYDROXY-CYSTEINE
    "DA2": "ARG",  # DA2 ARG  MODIFIED ARGININE
    "DAB": "ALA",  # DAB ALA  2,4-DIAMINOBUTYRIC ACID
    "DAH": "PHE",  # DAH PHE  3,4-DIHYDROXYDAHNYLALANINE
    "DAL": "ALA",  # DAL ALA  D-ALANINE
    "DAM": "ALA",  # DAM ALA  N-METHYL-ALPHA-BETA-DEHYDROALANINE
    "DAR": "ARG",  # DAR ARG  D-ARGININE
    "DAS": "ASP",  # DAS ASP  D-ASPARTIC ACID
    "DBU": "ALA",  # DBU ALA  (2E)-2-AMINOBUT-2-ENOIC ACID
    "DBY": "TYR",  # DBY TYR  3,5 DIBROMOTYROSINE
    "DBZ": "ALA",  # DBZ ALA  3-(BENZOYLAMINO)-L-ALANINE
    "DCL": "LEU",  # DCL LEU  2-AMINO-4-METHYL-PENTANYL GROUP
    "DCY": "CYS",  # DCY CYS  D-CYSTEINE
    "DDE": "HIS",  # DDE HIS
    "DGL": "GLU",  # DGL GLU  D-GLU
    "DGN": "GLN",  # DGN GLN  D-GLUTAMINE
    "DHA": "ALA",  # DHA ALA  2-AMINO-ACRYLIC ACID
    "DHI": "HIS",  # DHI HIS  D-HISTIDINE
    "DHL": "SER",  # DHL SER  POST-TRANSLATIONAL MODIFICATION
    "DIC": "ASP",  # DIC ASP
    "DID": "ASP",  # DIC ASP
    "DIL": "ILE",  # DIL ILE  D-ISOLEUCINE
    "DIV": "VAL",  # DIV VAL  D-ISOVALINE
    "DLE": "LEU",  # DLE LEU  D-LEUCINE
    "DLS": "LYS",  # DLS LYS  DI-ACETYL-LYSINE
    "DLY": "LYS",  # DLY LYS  D-LYSINE
    "DMH": "ASN",  # DMH ASN  N4,N4-DIMETHYL-ASPARAGINE
    "DMK": "ASP",  # DMK ASP  DIMETHYL ASPARTIC ACID
    "DNE": "LEU",  # DNE LEU  D-NORLEUCINE
    "DNG": "LEU",  # DNG LEU  N-FORMYL-D-NORLEUCINE
    "DNL": "LYS",  # DNL LYS  6-AMINO-HEXANAL
    "DNM": "LEU",  # DNM LEU  D-N-METHYL NORLEUCINE
    "DPH": "PHE",  # DPH PHE  DEAMINO-METHYL-PHENYLALANINE
    "DPL": "PRO",  # DPL PRO  4-OXOPROLINE
    "DPN": "PHE",  # DPN PHE  D-CONFIGURATION
    "DPP": "ALA",  # DPP ALA  DIAMMINOPROPANOIC ACID
    "DPQ": "TYR",  # DPQ TYR  TYROSINE DERIVATIVE
    "DPR": "PRO",  # DPR PRO  D-PROLINE
    "DSE": "SER",  # DSE SER  D-SERINE N-METHYLATED
    "DSG": "ASN",  # DSG ASN  D-ASPARAGINE
    "DSN": "SER",  # DSN SER  D-SERINE
    "DTH": "THR",  # DTH THR  D-THREONINE
    "DTR": "TRP",  # DTR TRP  D-TRYPTOPHAN
    "DTY": "TYR",  # DTY TYR  D-TYROSINE
    "DVA": "VAL",  # DVA VAL  D-VALINE
    "DYG": "ALA",  # DYG ALA
    "DYS": "CYS",  # DYS CYS
    "EFC": "CYS",  # EFC CYS  S,S-(2-FLUOROETHYL)THIOCYSTEINE
    "ESB": "TYR",  # ESB TYR
    "ESC": "MET",  # ESC MET  2-AMINO-4-ETHYL SULFANYL BUTYRIC ACID
    "FCL": "PHE",  # FCL PHE  3-CHLORO-L-PHENYLALANINE
    "FGL": "ALA",  # FGL ALA  2-AMINOPROPANEDIOIC ACID
    "FGP": "SER",  # FGP SER
    "FHL": "LYS",  # FHL LYS  MODIFIED LYSINE
    "FLE": "LEU",  # FLE LEU  FUROYL-LEUCINE
    "FLT": "TYR",  # FLT TYR  FLUOROMALONYL TYROSINE
    "FME": "MET",  # FME MET  FORMYL-METHIONINE
    "FOE": "CYS",  # FOE CYS
    "FOG": "PHE",  # FOG PHE  PHENYLALANINOYL-[1-HYDROXY]-2-PROPYLENE
    "FOR": "MET",  # FOR MET
    "FRF": "PHE",  # FRF PHE  PHE FOLLOWED BY REDUCED PHE
    "FTR": "TRP",  # FTR TRP  FLUOROTRYPTOPHANE
    "FTY": "TYR",  # FTY TYR  DEOXY-DIFLUOROMETHELENE-PHOSPHOTYROSINE
    "GHG": "GLN",  # GHG GLN  GAMMA-HYDROXY-GLUTAMINE
    "GHP": "GLY",  # GHP GLY  4-HYDROXYPHENYLGLYCINE
    "GL3": "GLY",  # GL3 GLY  POST-TRANSLATIONAL MODIFICATION
    "GLH": "GLN",  # GLH GLN
    "GLM": "GLU",  # GLM GLU
    "GLN": "GLN",  # GLN GLN
    "GLO": "GLN",  # GLO GLN
    "GLU": "GLU",  # GLU GLU
    "GLV": "GLU",  # GLV GLU
    "GLY": "GLY",  # GLY GLY
    "GLZ": "GLY",  # GLZ GLY  AMINO-ACETALDEHYDE
    "GMA": "GLU",  # GMA GLU  1-AMIDO-GLUTAMIC ACID
    "GMU": "ALA",  # GMU 5MU
    "GPL": "LYS",  # GPL LYS  LYSINE GUANOSINE-5'-MONOPHOSPHATE
    "GT9": "CYS",  # GT9 CYS  SG ALKYLATED
    "GVL": "SER",  # GVL SER  SERINE MODIFED WITH PHOSPHOPANTETHEINE
    "GYC": "CYS",  # GYC CYS
    "GYS": "GLY",  # GYS GLY
    "H5M": "PRO",  # H5M PRO  TRANS-3-HYDROXY-5-METHYLPROLINE
    "HHK": "ALA",  # HHK ALA  (2S)-2,8-DIAMINOOCTANOIC ACID
    "HIA": "HIS",  # HIA HIS  L-HISTIDINE AMIDE
    "HIC": "HIS",  # HIC HIS  4-METHYL-HISTIDINE
    "HIP": "HIS",  # HIP HIS  ND1-PHOSPHONOHISTIDINE
    "HIQ": "HIS",  # HIQ HIS  MODIFIED HISTIDINE
    "HIS": "HIS",  # HIS HIS
    "HID": "HIS",  # HID HIS
    "HIE": "HIS",  # HID HIS
    "HIN": "HIS",  # HID HIS
    "HIY": "HIS",  # HIY HIS
    "HIZ": "HIS",  # HIZ HIS
    "HSD": "HIS",  # HID HIS
    "HSP": "HIS",  # HID HIS
    "HSE": "HIS",  # HID HIS
    "HLU": "LEU",  # HLU LEU  BETA-HYDROXYLEUCINE
    "HMF": "ALA",  # HMF ALA  2-AMINO-4-PHENYL-BUTYRIC ACID
    "HMR": "ARG",  # HMR ARG  BETA-HOMOARGININE
    "HPE": "PHE",  # HPE PHE  HOMOPHENYLALANINE
    "HPH": "PHE",  # HPH PHE  PHENYLALANINOL GROUP
    "HPQ": "PHE",  # HPQ PHE  HOMOPHENYLALANINYLMETHANE
    "HRG": "ARG",  # HRG ARG  L-HOMOARGININE
    "HSL": "SER",  # HSL SER  HOMOSERINE LACTONE
    "HSO": "HIS",  # HSO HIS  HISTIDINOL
    "HTI": "CYS",  # HTI CYS
    "HTR": "TRP",  # HTR TRP  BETA-HYDROXYTRYPTOPHANE
    "HY3": "PRO",  # HY3 PRO  3-HYDROXYPROLINE
    "HYP": "PRO",  # HYP PRO  4-HYDROXYPROLINE
    "IAM": "ALA",  # IAM ALA  4-[(ISOPROPYLAMINO)METHYL]PHENYLALANINE
    "IAS": "ASP",  # IAS ASP  ASPARTYL GROUP
    "IGL": "ALA",  # IGL ALA  ALPHA-AMINO-2-INDANACETIC ACID
    "IIL": "ILE",  # IIL ILE  ISO-ISOLEUCINE
    "ILE": "ILE",  # ILE ILE
    "ILG": "GLU",  # ILG GLU  GLU LINKED TO NEXT RESIDUE VIA CG
    "ILX": "ILE",  # ILX ILE  4,5-DIHYDROXYISOLEUCINE
    "IML": "ILE",  # IML ILE  N-METHYLATED
    "IPG": "GLY",  # IPG GLY  N-ISOPROPYL GLYCINE
    "IT1": "LYS",  # IT1 LYS
    "IYR": "TYR",  # IYR TYR  3-IODO-TYROSINE
    "KCX": "LYS",  # KCX LYS  CARBAMOYLATED LYSINE
    "KGC": "LYS",  # KGC LYS
    "KOR": "CYS",  # KOR CYS  MODIFIED CYSTEINE
    "KPI": "LYS",
    "KST": "LYS",  # KST LYS  N~6~-(5-CARBOXY-3-THIENYL)-L-LYSINE
    "KYN": "ALA",  # KYN ALA  KYNURENINE
    "LA2": "LYS",  # LA2 LYS
    "LAL": "ALA",  # LAL ALA  N,N-DIMETHYL-L-ALANINE
    "LCK": "LYS",  # LCK LYS
    "LCX": "LYS",  # LCX LYS  CARBAMYLATED LYSINE
    "LDH": "LYS",  # LDH LYS  N~6~-ETHYL-L-LYSINE
    "LED": "LEU",  # LED LEU  POST-TRANSLATIONAL MODIFICATION
    "LEF": "LEU",  # LEF LEU  2-5-FLUOROLEUCINE
    "LET": "LYS",  # LET LYS  ODIFIED LYSINE
    "LEU": "LEU",  # LEU LEU
    "LEV": "LEU",  # LEV LEU
    "LLP": "LYS",  # LLP LYS
    "LLY": "LYS",  # LLY LYS  NZ-(DICARBOXYMETHYL)LYSINE
    "LME": "GLU",  # LME GLU  (3R)-3-METHYL-L-GLUTAMIC ACID
    "LNT": "LEU",  # LNT LEU
    "LPD": "PRO",  # LPD PRO  L-PROLINAMIDE
    "LSO": "LYS",  # LSO LYS  MODIFIED LYSINE
    "LYM": "LYS",  # LYM LYS  DEOXY-METHYL-LYSINE
    "LYN": "LYS",  # LYN LYS  2,6-DIAMINO-HEXANOIC ACID AMIDE
    "LYP": "LYS",  # LYP LYS  N~6~-METHYL-N~6~-PROPYL-L-LYSINE
    "LYR": "LYS",  # LYR LYS  MODIFIED LYSINE
    "LYS": "LYS",  # LYS LYS
    "LYX": "LYS",  # LYX LYS  N''-(2-COENZYME A)-PROPANOYL-LYSINE
    "LYZ": "LYS",  # LYZ LYS  5-HYDROXYLYSINE
    "M0H": "CYS",  # M0H CYS  S-(HYDROXYMETHYL)-L-CYSTEINE
    "M2L": "LYS",  # M2L LYS
    "M3L": "LYS",  # M3L LYS  N-TRIMETHYLLYSINE
    "MAA": "ALA",  # MAA ALA  N-METHYLALANINE
    "MAI": "ARG",  # MAI ARG  DEOXO-METHYLARGININE
    "MBQ": "TYR",  # MBQ TYR
    "MC1": "SER",  # MC1 SER  METHICILLIN ACYL-SERINE
    "MCL": "LYS",  # MCL LYS  NZ-(1-CARBOXYETHYL)-LYSINE
    "MCS": "CYS",  # MCS CYS  MALONYLCYSTEINE
    "MDO": "ALA",  # MDO ALA
    "MEA": "PHE",  # MEA PHE  N-METHYLPHENYLALANINE
    "MEG": "GLU",  # MEG GLU  (2S,3R)-3-METHYL-GLUTAMIC ACID
    "MEN": "ASN",  # MEN ASN  GAMMA METHYL ASPARAGINE
    "MEQ": "GLN",
    "MET": "MET",  # MET MET
    "MEU": "GLY",  # MEU GLY  O-METHYL-GLYCINE
    "MFC": "ALA",  # MFC ALA  CYCLIZED
    "MGG": "ARG",  # MGG ARG  MODIFIED D-ARGININE
    "MGN": "GLN",  # MGN GLN  2-METHYL-GLUTAMINE
    "MHL": "LEU",  # MHL LEU  N-METHYLATED, HYDROXY
    "MHO": "MET",  # MHO MET  POST-TRANSLATIONAL MODIFICATION
    "MHS": "HIS",  # MHS HIS  1-N-METHYLHISTIDINE
    "MIS": "SER",  # MIS SER  MODIFIED SERINE
    "MIR": "SER",
    "MLE": "LEU",  # MLE LEU  N-METHYLATED
    "MLL": "LEU",  # MLL LEU  METHYL L-LEUCINATE
    "MLY": "LYS",  # MLY LYS  METHYLATED LYSINE
    "MLZ": "LYS",  # MLZ LYS  N-METHYL-LYSINE
    "MME": "MET",  # MME MET  N-METHYL METHIONINE
    "MNL": "LEU",  # MNL LEU  4,N-DIMETHYLNORLEUCINE
    "MNV": "VAL",  # MNV VAL  N-METHYL-C-AMINO VALINE
    "MPQ": "GLY",  # MPQ GLY  N-METHYL-ALPHA-PHENYL-GLYCINE
    "MSA": "GLY",  # MSA GLY  (2-S-METHYL) SARCOSINE
    "MSE": "MET",  # MSE MET  ELENOMETHIONINE
    "MSO": "MET",  # MSO MET  METHIONINE SULFOXIDE
    "MTY": "PHE",  # MTY PHE  3-HYDROXYPHENYLALANINE
    "MVA": "VAL",  # MVA VAL  N-METHYLATED
    "N10": "SER",  # N10 SER  O-[(HEXYLAMINO)CARBONYL]-L-SERINE
    "NAL": "ALA",  # NAL ALA  BETA-(2-NAPHTHYL)-ALANINE
    "NAM": "ALA",  # NAM ALA  NAM NAPTHYLAMINOALANINE
    "NBQ": "TYR",  # NBQ TYR
    "NC1": "SER",  # NC1 SER  NITROCEFIN ACYL-SERINE
    "NCB": "ALA",  # NCB ALA  CHEMICAL MODIFICATION
    "NEP": "HIS",  # NEP HIS  N1-PHOSPHONOHISTIDINE
    "NFA": "PHE",  # NFA PHE  MODIFIED PHENYLALANINE
    "NIY": "TYR",  # NIY TYR  META-NITRO-TYROSINE
    "NLE": "LEU",  # NLE LEU  NORLEUCINE
    "NLN": "LEU",  # NLN LEU  NORLEUCINE AMIDE
    "NLO": "LEU",  # NLO LEU  O-METHYL-L-NORLEUCINE
    "NMC": "GLY",  # NMC GLY  N-CYCLOPROPYLMETHYL GLYCINE
    "NMM": "ARG",  # NMM ARG  MODIFIED ARGININE
    "NPH": "CYS",  # NPH CYS
    "NRQ": "ALA",  # NRQ ALA
    "NVA": "VAL",  # NVA VAL  NORVALINE
    "NYC": "ALA",  # NYC ALA
    "NYS": "CYS",  # NYS CYS
    "NZH": "HIS",  # NZH HIS
    "OAS": "SER",  # OAS SER  O-ACETYLSERINE
    "OBS": "LYS",  # OBS LYS  MODIFIED LYSINE
    "OCS": "CYS",  # OCS CYS  CYSTEINE SULFONIC ACID
    "OCY": "CYS",  # OCY CYS  HYDROXYETHYLCYSTEINE
    "OHI": "HIS",  # OHI HIS  3-(2-OXO-2H-IMIDAZOL-4-YL)-L-ALANINE
    "OHS": "ASP",  # OHS ASP  O-(CARBOXYSULFANYL)-4-OXO-L-HOMOSERINE
    "OLT": "THR",  # OLT THR  O-METHYL-L-THREONINE
    "OMT": "MET",  # OMT MET  METHIONINE SULFONE
    "OPR": "ARG",  # OPR ARG  C-(3-OXOPROPYL)ARGININE
    "ORN": "ALA",  # ORN ALA  ORNITHINE
    "ORQ": "ARG",  # ORQ ARG  N~5~-ACETYL-L-ORNITHINE
    "OSE": "SER",  # OSE SER  O-SULFO-L-SERINE
    "OTY": "TYR",  # OTY TYR
    "OXX": "ASP",  # OXX ASP  OXALYL-ASPARTYL ANHYDRIDE
    "P1L": "CYS",  # P1L CYS  S-PALMITOYL CYSTEINE
    "P2Y": "PRO",  # P2Y PRO  (2S)-PYRROLIDIN-2-YLMETHYLAMINE
    "PAQ": "TYR",  # PAQ TYR  SEE REMARK 999
    "PAT": "TRP",  # PAT TRP  ALPHA-PHOSPHONO-TRYPTOPHAN
    "PBB": "CYS",  # PBB CYS  S-(4-BROMOBENZYL)CYSTEINE
    "PBF": "PHE",  # PBF PHE  PARA-(BENZOYL)-PHENYLALANINE
    "PCA": "PRO",  # PCA PRO  5-OXOPROLINE
    "PCS": "PHE",  # PCS PHE  PHENYLALANYLMETHYLCHLORIDE
    "PEC": "CYS",  # PEC CYS  S,S-PENTYLTHIOCYSTEINE
    "PF5": "PHE",  # PF5 PHE  2,3,4,5,6-PENTAFLUORO-L-PHENYLALANINE
    "PFF": "PHE",  # PFF PHE  4-FLUORO-L-PHENYLALANINE
    "PG1": "SER",  # PG1 SER  BENZYLPENICILLOYL-ACYLATED SERINE
    "PG9": "GLY",  # PG9 GLY  D-PHENYLGLYCINE
    "PHA": "PHE",  # PHA PHE  PHENYLALANINAL
    "PHD": "ASP",  # PHD ASP  2-AMINO-4-OXO-4-PHOSPHONOOXY-BUTYRIC ACID
    "PHE": "PHE",  # PHE PHE
    "PHI": "PHE",  # PHI PHE  IODO-PHENYLALANINE
    "PHL": "PHE",  # PHL PHE  L-PHENYLALANINOL
    "PHM": "PHE",  # PHM PHE  PHENYLALANYLMETHANE
    "PIA": "ALA",  # PIA ALA  FUSION OF ALA 65, TYR 66, GLY 67
    "PLE": "LEU",  # PLE LEU  LEUCINE PHOSPHINIC ACID
    "PM3": "PHE",  # PM3 PHE
    "POM": "PRO",  # POM PRO  CIS-5-METHYL-4-OXOPROLINE
    "PPH": "LEU",  # PPH LEU  PHENYLALANINE PHOSPHINIC ACID
    "PPN": "PHE",  # PPN PHE  THE LIGAND IS A PARA-NITRO-PHENYLALANINE
    "PR3": "CYS",  # PR3 CYS  INE DTT-CYSTEINE
    "PRO": "PRO",  # PRO PRO
    "PRQ": "PHE",  # PRQ PHE  PHENYLALANINE
    "PRR": "ALA",  # PRR ALA  3-(METHYL-PYRIDINIUM)ALANINE
    "PRS": "PRO",  # PRS PRO  THIOPROLINE
    "PSA": "PHE",  # PSA PHE
    "PSH": "HIS",  # PSH HIS  1-THIOPHOSPHONO-L-HISTIDINE
    "PTH": "TYR",  # PTH TYR  METHYLENE-HYDROXY-PHOSPHOTYROSINE
    "PTM": "TYR",  # PTM TYR  ALPHA-METHYL-O-PHOSPHOTYROSINE
    "PTR": "TYR",  # PTR TYR  O-PHOSPHOTYROSINE
    "PYA": "ALA",  # PYA ALA  3-(1,10-PHENANTHROL-2-YL)-L-ALANINE
    "PYC": "ALA",  # PYC ALA  PYRROLE-2-CARBOXYLATE
    "PYR": "SER",  # PYR SER  CHEMICALLY MODIFIED
    "PYT": "ALA",  # PYT ALA  MODIFIED ALANINE
    "PYX": "CYS",  # PYX CYS  S-[S-THIOPYRIDOXAMINYL]CYSTEINE
    "R1A": "CYS",  # R1A CYS
    "R1B": "CYS",  # R1B CYS
    "R1F": "CYS",  # R1F CYS
    "R7A": "CYS",  # R7A CYS
    "RC7": "ALA",  # RC7 ALA
    "RCY": "CYS",  # RCY CYS
    "S1H": "SER",  # S1H SER  1-HEXADECANOSULFONYL-O-L-SERINE
    "SAC": "SER",  # SAC SER  N-ACETYL-SERINE
    "SAH": "CYS",  # SAH CYS  S-ADENOSYL-L-HOMOCYSTEINE
    "SAR": "GLY",  # SAR GLY  SARCOSINE
    "SBD": "SER",  # SBD SER
    "SBG": "SER",  # SBG SER  MODIFIED SERINE
    "SBL": "SER",  # SBL SER
    "SC2": "CYS",  # SC2 CYS  N-ACETYL-L-CYSTEINE
    "SCH": "CYS",  # SCH CYS  S-METHYL THIOCYSTEINE GROUP
    "SCS": "CYS",  # SCS CYS  MODIFIED CYSTEINE
    "SCY": "CYS",  # SCY CYS  CETYLATED CYSTEINE
    "SYS": "CYS",
    "SDP": "SER",  # SDP SER
    "SEB": "SER",  # SEB SER  O-BENZYLSULFONYL-SERINE
    "SEC": "ALA",  # SEC ALA  2-AMINO-3-SELENINO-PROPIONIC ACID
    "SEL": "SER",  # SEL SER  2-AMINO-1,3-PROPANEDIOL
    "SEM": "SER",  # SEM SER
    "SEP": "SER",  # SEP SER  E PHOSPHOSERINE
    "SER": "SER",  # SER SER
    "SET": "SER",  # SET SER  AMINOSERINE
    "SGB": "SER",  # SGB SER  MODIFIED SERINE
    "SGR": "SER",  # SGR SER  MODIFIED SERINE
    "SHC": "CYS",  # SHC CYS  S-HEXYLCYSTEINE
    "SHP": "GLY",  # SHP GLY  (4-HYDROXYMALTOSEPHENYL)GLYCINE
    "SIC": "ALA",  # SIC ALA
    "SLZ": "LYS",  # SLZ LYS  L-THIALYSINE
    "SMC": "CYS",  # SMC CYS  POST-TRANSLATIONAL MODIFICATION
    "SME": "MET",  # SME MET  METHIONINE SULFOXIDE
    "SMF": "PHE",  # SMF PHE  4-SULFOMETHYL-L-PHENYLALANINE
    "SNC": "CYS",  # SNC CYS  S-NITROSO CYSTEINE
    "SNN": "ASP",  # SNN ASP  POST-TRANSLATIONAL MODIFICATION
    "SOC": "CYS",  # SOC CYS  DIOXYSELENOCYSTEINE
    "SOY": "SER",  # SOY SER  OXACILLOYL-ACYLATED SERINE
    "SUI": "ALA",  # SUI ALA
    "SUN": "SER",  # SUN SER  TABUN CONJUGATED SERINE
    "SVA": "SER",  # SVA SER  SERINE VANADATE
    "SVV": "SER",  # SVV SER  MODIFIED SERINE
    "SVX": "SER",  # SVX SER  MODIFIED SERINE
    "SVY": "SER",  # SVY SER  MODIFIED SERINE
    "SVZ": "SER",  # SVZ SER  MODIFIED SERINE
    "SXE": "SER",  # SXE SER  MODIFIED SERINE
    "TBG": "GLY",  # TBG GLY  T-BUTYL GLYCINE
    "TBM": "THR",  # TBM THR
    "TCQ": "TYR",  # TCQ TYR  MODIFIED TYROSINE
    "TEE": "CYS",  # TEE CYS  POST-TRANSLATIONAL MODIFICATION
    "TH5": "THR",  # TH5 THR  O-ACETYL-L-THREONINE
    "THC": "THR",  # THC THR  N-METHYLCARBONYLTHREONINE
    "THR": "THR",  # THR THR
    "TIH": "ALA",  # TIH ALA  BETA(2-THIENYL)ALANINE
    "TMD": "THR",  # TMD THR  N-METHYLATED, EPSILON C ALKYLATED
    "TNB": "CYS",  # TNB CYS  S-(2,3,6-TRINITROPHENYL)CYSTEINE
    "TOX": "TRP",  # TOX TRP
    "TPL": "TRP",  # TPL TRP  TRYTOPHANOL
    "TPO": "THR",  # TPO THR  HOSPHOTHREONINE
    "TPQ": "ALA",  # TPQ ALA  2,4,5-TRIHYDROXYPHENYLALANINE
    "TQQ": "TRP",  # TQQ TRP
    "TRF": "TRP",  # TRF TRP  N1-FORMYL-TRYPTOPHAN
    "TRN": "TRP",  # TRN TRP  AZA-TRYPTOPHAN
    "TRO": "TRP",  # TRO TRP  2-HYDROXY-TRYPTOPHAN
    "TRP": "TRP",  # TRP TRP
    "TRQ": "TRP",  # TRQ TRP
    "TRW": "TRP",  # TRW TRP
    "TRX": "TRP",  # TRX TRP  6-HYDROXYTRYPTOPHAN
    "TTQ": "TRP",  # TTQ TRP  6-AMINO-7-HYDROXY-L-TRYPTOPHAN
    "TTS": "TYR",  # TTS TYR
    "TY2": "TYR",  # TY2 TYR  3-AMINO-L-TYROSINE
    "TY3": "TYR",  # TY3 TYR  3-HYDROXY-L-TYROSINE
    "TYB": "TYR",  # TYB TYR  TYROSINAL
    "TYC": "TYR",  # TYC TYR  L-TYROSINAMIDE
    "TYI": "TYR",  # TYI TYR  3,5-DIIODOTYROSINE
    "TYM": "TYR",  # TYM TYR
    "TYN": "TYR",  # TYN TYR  ADDUCT AT HYDROXY GROUP
    "TYO": "TYR",  # TYO TYR
    "TYQ": "TYR",  # TYQ TYR  AMINOQUINOL FORM OF TOPA QUINONONE
    "TYR": "TYR",  # TYR TYR
    "TYS": "TYR",  # TYS TYR  INE SULPHONATED TYROSINE
    "TYT": "TYR",  # TYT TYR
    "TYX": "CYS",  # TYX CYS  S-(2-ANILINO-2-OXOETHYL)-L-CYSTEINE
    "TYY": "TYR",  # TYY TYR  IMINOQUINONE FORM OF TOPA QUINONONE
    "TYZ": "ARG",  # TYZ ARG  PARA ACETAMIDO BENZOIC ACID
    "UMA": "ALA",  # UMA ALA
    "VAD": "VAL",  # VAD VAL  DEAMINOHYDROXYVALINE
    "VAF": "VAL",  # VAF VAL  METHYLVALINE
    "VAL": "VAL",  # VAL VAL
    "VDL": "VAL",  # VDL VAL  (2R,3R)-2,3-DIAMINOBUTANOIC ACID
    "VLL": "VAL",  # VLL VAL  (2S)-2,3-DIAMINOBUTANOIC ACID
    "VME": "VAL",  # VME VAL  O- METHYLVALINE
    "X9Q": "ALA",  # X9Q ALA
    "XX1": "LYS",  # XX1 LYS  N~6~-7H-PURIN-6-YL-L-LYSINE
    "XXY": "ALA",  # XXY ALA
    "XYG": "ALA",  # XYG ALA
    "YCM": "CYS",  # YCM CYS  S-(2-AMINO-2-OXOETHYL)-L-CYSTEINE
    "YOF": "TYR",  # YOF TYR  3-FLUOROTYROSINE
}


#
@dataclass
class Residue:
    atom_num: int = 0
    atom_coords: np.ndarray = np.zeros((14, 4))

    def __post_init__(self):
        self.atom_coords.fill(np.nan)
        self.atom_coords[:, 3] = 0.0


@dataclass
class Chain:
    res_num: list[str] = field(default_factory=list)
    res_id: list[int] = field(default_factory=list)
    res_one: list[str] = field(default_factory=list)
    res_name: list[str] = field(default_factory=list)
    res_class: list[int] = field(default_factory=list)
    coord: list[np.ndarray] = field(default_factory=list)


@dataclass
class Prev:
    m_num: int = 0
    alt: str = "@"
    res_num: str = "@"
    res_id: int = 0
    res_one: str = "@"
    res_name: str = "@"
    chain: str = "@"


@dataclass
class Structure:
    chains: list[str] = field(default_factory=list)
    res_num: dict[str, list] = field(default_factory=dict)
    res_id: dict[str, list] = field(default_factory=dict)
    res_one: dict[str, list] = field(default_factory=dict)
    res_name: dict[str, list] = field(default_factory=dict)
    res_class: dict[str, list] = field(default_factory=dict)
    coord: dict[str, np.ndarray] = field(default_factory=dict)


class CustomPDB:
    def __init__(
        self,
        pdb_fn: Union[str, Path],
        mod2std: bool = False,
    ):
        self.pdb_fn = pdb_fn
        self.mod2std = mod2std
        self.pdb_infos, self.pdb_lines = self.infos()

    def read_line(
        self,
        line: str,
        prev: Prev,
        residue: Residue,
    ):
        prev.alt = line[16]
        prev.res_num = line[22:27].strip()
        prev.res_name = line[17:20].strip()
        if self.mod2std and prev.res_name in modres:
            prev.res_name = modres[prev.res_name]
        elif prev.res_name not in STANDARD_ID:
            prev.res_name = "UNK"
        prev.res_id = STANDARD_ID[prev.res_name]
        prev.res_one = STANDARD_inv[prev.res_name]
        prev.chain = line[21]
        #
        residue.atom_coords[residue.atom_num, :3] = np.double(
            [line[30:38], line[38:46], line[46:54]]  # type: ignore
        )
        residue.atom_coords[residue.atom_num, 3] = atom_types.index(line[12:16].strip())
        residue.atom_num += 1
        return prev, residue

    def append_res(
        self,
        prev: Prev,
        chain: Chain,
        residue: Residue,
    ):
        chain.res_num.append(prev.res_num)
        chain.res_id.append(prev.res_id)
        chain.res_one.append(prev.res_one)
        chain.res_name.append(prev.res_name)
        chain.res_class.append(classification[prev.res_name])
        chain.coord.append(residue.atom_coords.copy())
        return chain

    def append_ch(
        self,
        prev: Prev,
        chain: Chain,
        struc: Structure,
    ):
        struc.chains.append(prev.chain)
        struc.res_num[prev.chain] = chain.res_num
        struc.res_id[prev.chain] = chain.res_id
        struc.res_one[prev.chain] = chain.res_one
        struc.res_name[prev.chain] = chain.res_name
        struc.res_class[prev.chain] = chain.res_class
        struc.coord[prev.chain] = np.stack(chain.coord, axis=0)
        return struc

    def split_pdb(self):
        m = 0
        read = {m: list()}
        with open(self.pdb_fn, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("MODEL"):
                    m = int(line.split()[1])
                    read[m] = list()
                elif line.startswith("ATOM"):
                    read[m].append(line)

        output = dict()
        m_idx = 0
        for m in read:
            output[m_idx] = read[m]
            m_idx += 1

        return output

    def infos(self):
        # init
        m_num = 0
        lines = list()
        first = True
        first_model = True

        struc = Structure()
        chain = Chain()
        residue = Residue()
        prev = Prev(m_num=m_num)

        pdb_infos = dict()
        pdb_lines = dict()

        # read
        with open(self.pdb_fn) as f:
            for line in f:
                if line.startswith("MODEL"):
                    # Save previous model
                    if prev.res_name != "@":
                        chain = self.append_res(prev, chain, residue)
                        struc = self.append_ch(prev, chain, struc)
                    if not first_model:
                        pdb_infos[prev.m_num] = struc
                        pdb_lines[prev.m_num] = lines

                    # Re-init
                    m_num = int(line.split()[1])
                    lines = list()
                    first = True
                    first_model = False

                    struc = Structure()
                    chain = Chain()
                    residue = Residue()
                    prev = Prev(m_num=m_num)

                elif line.startswith("ATOM"):
                    now_atom = line[12:16].strip()
                    now_alt = line[16]
                    now_res_name = line[17:20].strip()
                    now_ch = line[21]
                    now_res_num = line[22:27].strip()
                    if line[12:16].strip() not in atom_types:
                        continue

                    if first:
                        first = False
                        lines.append(line.strip())
                        prev, residue = self.read_line(line, prev, residue)
                        continue

                    elif now_ch != prev.chain:
                        chain = self.append_res(prev, chain, residue)
                        struc = self.append_ch(prev, chain, struc)
                        #
                        chain = Chain()
                        residue = Residue()

                    elif now_res_num != prev.res_num:
                        chain = self.append_res(prev, chain, residue)
                        residue = Residue()

                    elif now_alt != prev.alt:
                        if now_res_name != prev.res_name:
                            continue
                        if atom_types.index(now_atom) in residue.atom_coords[:, 3]:
                            continue  # use only first alternative atom, but if the atom it not in residue, append!

                    else:
                        if now_res_name != prev.res_name:
                            continue
                        if atom_types.index(now_atom) in residue.atom_coords[:, 3]:
                            continue

                    lines.append(line.strip())
                    prev, residue = self.read_line(line, prev, residue)

            # Save the last model
            if prev.res_name != "@":
                chain = self.append_res(prev, chain, residue)
                struc = self.append_ch(prev, chain, struc)
            pdb_infos[m_num] = struc
            pdb_lines[m_num] = lines

        # Check if the structure is empty
        if np.all(np.array([len(pdb_infos[num].chains) for num in pdb_infos]) == 0):
            print(self.pdb_fn, ": No structure found in the PDB file")
            raise RuntimeError

        else:
            out_infos = dict()
            out_lines = dict()
            for i, k in enumerate(list(pdb_infos.keys())):
                out_infos[i] = pdb_infos[k]
                out_lines[i] = pdb_lines[k]
            return out_infos, out_lines

    def write_refined_pdb(
        self, new_fn: Union[str, None] = None, only_first_model: bool = True
    ):
        if new_fn is None:
            new_fn = str(self.pdb_fn)
            new_fn = new_fn.replace(".pdb", "_refined.pdb")

        with open(new_fn, "w") as f:
            for m in self.pdb_lines:
                wrt = list()
                for line in self.pdb_lines[m]:
                    wrt.append(line)
                to_write = "\n".join(wrt)
                if only_first_model:
                    f.write(to_write)
                    break
                else:
                    f.write(f"MODEL {m}\n")
                    f.write(to_write)
                    f.write("ENDMDL\n")

    def renum_pdb(self):
        pdb_infos = self.pdb_infos
        pdb_lines = self.pdb_lines

        renum_map = dict()
        for m in pdb_infos:
            renum_map[m] = dict()
            for ch in pdb_infos[m].chains:
                renum_map[m][ch] = dict()
                for i, res_num in enumerate(pdb_infos[m].res_num[ch]):
                    renum_map[m][ch][res_num] = i + 1

        new_lines = dict()
        for m in pdb_lines:
            new_lines[m] = dict()
            for line in pdb_lines[m]:
                ch = line[21]
                if ch not in new_lines[m]:
                    new_lines[m][ch] = list()
                res_num = line[22:27].strip()
                new_res_num = f"{renum_map[m][ch][res_num]} "
                new_lines[m][ch].append(f"{line[:22]}{new_res_num:>5s}{line[27:]}")

        return new_lines, renum_map

    def write_renum_pdb(
        self,
        new_fn: Union[str, None] = None,
        return_result: bool = False,
        only_first_model: bool = True,
    ):
        if new_fn is None:
            new_fn = str(self.pdb_fn)
            new_fn = new_fn.replace(".pdb", "_renum.pdb")

        renum_lines, renum_map = self.renum_pdb()
        with open(new_fn, "w") as f:
            for m in renum_lines:
                if only_first_model:
                    for ch in renum_lines[m]:
                        f.write("\n".join(renum_lines[m][ch]) + "\n")
                        f.write("TER\n")
                    break
                else:
                    f.write(f"MODEL {m + 1}\n")
                    for ch in renum_lines[m]:
                        f.write("\n".join(renum_lines[m][ch]) + "\n")
                        f.write("TER\n")
                    f.write("ENDMDL\n")

        map_fn = str(self.pdb_fn)
        map_fn = map_fn.replace(".pdb", "_renum_map.json")
        with open(map_fn, "w") as f:
            json.dump(renum_map, f)

        if return_result:
            return renum_lines, renum_map
