# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Изпраща се от процесния endpoint когато един или повече модули са били инспектирани. Включва информация за преминаване/неуспех,
както и подробен доклад от инспекцията, включително конкретните измервания и проверки, които са били направени,
и дефектите, които са били открити по време на процеса.

Обща инспекция (2 Circuit PCB Panel инспектиран чрез AOI):
{
   "TransactionId": "14d48338-09b7-4d20-acb9-bf951270793a",
   "InspectionMethod": "AOI",
   "SamplingInformation": {
     "SamplingMethod": "NoSampling",
     "LotSize": null,
     "SampleSize": null
   },
   "Inspector": {
     "OperatorIdentifier": "BADGE489499",
     "ActorType": "Human",
     "LastName": "Smith",
     "FirstName": "Joseph",
     "LoginName": "joseph.smith@abcdrepairs.com"
   },
   "InspectedUnits": [
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 1,
       "OverallResult": "Passed",
       "Inspections": [
         {
           "UniqueIdentifier": "481f296f-d4b2-4d8e-8b05-a0a17ca33488",
           "InspectionName": "INSPECT_R21",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": []
         },
         {
           "UniqueIdentifier": "074c7aa5-8871-4629-b139-122b620bdc1b",
           "InspectionName": "INSPECT_R22",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": []
         }
       ]
     },
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 2,
       "OverallResult": "Failed",
       "Inspections": [
         {
           "UniqueIdentifier": "27e4a632-5670-4683-9b54-b67b7df98260",
           "InspectionName": "INSPECT_R21",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": []
         },
         {
           "UniqueIdentifier": "f7ed3609-ea35-4bcc-9170-cb5d540348d5",
           "InspectionName": "INSPECT_R22",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Failed",
           "Error": null,
           "DefectsFound": [
             {
               "UniqueIdentifier": "53c7d9e7-e43f-4415-a3ff-8932f0437dde",
               "DefectCode": "ISFSLD112",
               "DefectCategory": "Solder Problems",
               "Description": "Insuffiecient Solder on R22, Lead 1",
               "Comments": null,
               "ComponentOfInterest": {
                 "ReferenceDesignator": "R22.1",
                 "UnitPosition": null,
                 "PartNumber": "11123-8897"
               },
               "RegionOfInterest": {
                 "StartPointX": 0.0,
                 "StartPointY": 0.0,
                 "RegionSegments": []
               },
               "DefectImages": [
                 {
                   "MimeType": "image/jpg",
                   "ImageData": "rFRWd9iZ"
                 }
               ],
               "Priority": 1,
               "ConfidenceLevel": 100.0,
               "RelatedMeasurements": [],
               "RelatedSymptoms": []
             },
             {
               "UniqueIdentifier": "561d08c2-aac9-422a-8910-41a3528a8acc",
               "DefectCode": "TMBSTN211",
               "DefectCategory": "Solder Problems",
               "Description": "Tombston on R22",
               "Comments": null,
               "ComponentOfInterest": {
                 "ReferenceDesignator": "R22",
                 "UnitPosition": null,
                 "PartNumber": "11123-8897"
               },
               "RegionOfInterest": {
                 "StartPointX": 0.0,
                 "StartPointY": 0.0,
                 "RegionSegments": []
               },
               "DefectImages": [
                 {
                   "MimeType": "image/jpg",
                   "ImageData": "XSjjh8i5"
                 }
               ],
               "Priority": 1,
               "ConfidenceLevel": 100.0,
               "RelatedMeasurements": [],
               "RelatedSymptoms": []
             }
           ],
           "Symptoms": null,
           "Measurements": []
         },
         {
           "UniqueIdentifier": "abcbe17f-9232-4005-87e0-98651e2967b5",
           "InspectionName": "COSMETIC_INSPECTION",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Failed",
           "Error": null,
           "DefectsFound": [
             {
               "UniqueIdentifier": "8018a32b-ef92-494f-bb3d-5e0549bdea20",
               "DefectCode": "SCR23443",
               "DefectCategory": "Cosmetic Problems",
               "Description": "Scratch Detected on PCB substrate",
               "Comments": null,
               "ComponentOfInterest": {
                 "ReferenceDesignator": null,
                 "UnitPosition": null,
                 "PartNumber": null
               },
               "RegionOfInterest": {
                 "StartPointX": 2.3,
                 "StartPointY": 4.0,
                 "RegionSegments": [
                   {
                     "X": 5.6,
                     "Y": 4.0
                   },
                   {
                     "X": 5.6,
                     "Y": 1.6
                   },
                   {
                     "X": 2.3,
                     "Y": 1.6
                   },
                   {
                     "X": 2.3,
                     "Y": 4.0
                   }
                 ]
               },
               "DefectImages": [],
               "Priority": 1,
               "ConfidenceLevel": 100.0,
               "RelatedMeasurements": [],
               "RelatedSymptoms": []
             }
           ],
           "Symptoms": null,
           "Measurements": []
         }
       ]
     }
   ]
}

Пример за инспекция на спояваща паста (SPI):
{
   "TransactionId": "493bdbe0-9c32-4ed1-b7bf-b25372386b99",
   "InspectionMethod": "SPI",
   "SamplingInformation": {
     "SamplingMethod": "NoSampling",
     "LotSize": null,
     "SampleSize": null
   },
   "Inspector": {
     "OperatorIdentifier": "BADGE489499",
     "ActorType": "Human",
     "LastName": "Smith",
     "FirstName": "Joseph",
     "LoginName": "joseph.smith@abcdrepairs.com"
   },
   "InspectedUnits": [
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 1,
       "OverallResult": "Passed",
       "Inspections": [
         {
           "UniqueIdentifier": "09b88135-019d-44f0-b28d-1de766851fd1",
           "InspectionName": "INSPECT_PASTE_DEPOSITIONS",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": [
             {
               "$type": "CFX.Structures.SolderPasteInspection.SolderPasteMeasurement, CFX",
               "X": 5.62,
               "EX": 5.6,
               "Y": 8.29,
               "EY": 8.3,
               "Z": 5.01,
               "EZ": 5.0,
               "DX": 0.02,
               "DY": 0.03,
               "Vol": 5.11,
               "EVol": 5.1,
               "Image": null,
               "UniqueIdentifier": "9367a252-cd8b-4198-bd75-100a0ace2249",
               "MeasurementName": "R1.1",
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1.1"
             },
             {
               "$type": "CFX.Structures.SolderPasteInspection.SolderPasteMeasurement, CFX",
               "X": 5.62,
               "EX": 5.6,
               "Y": 8.29,
               "EY": 8.3,
               "Z": 5.01,
               "EZ": 5.0,
               "DX": 0.02,
               "DY": 0.03,
               "Vol": 5.11,
               "EVol": 5.1,
               "Image": null,
               "UniqueIdentifier": "db0d3ac0-b6b8-40c2-8dd4-2ca426d3373a",
               "MeasurementName": "R1.2",
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1.1"
             }
           ]
         }
       ]
     },
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 2,
       "OverallResult": "Failed",
       "Inspections": [
         {
           "UniqueIdentifier": "6ae0a4c5-119c-4381-8d9d-eb193345445f",
           "InspectionName": "INSPECT_PASTE_DEPOSITIONS",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": [
             {
               "$type": "CFX.Structures.SolderPasteInspection.SolderPasteMeasurement, CFX",
               "X": 5.62,
               "EX": 5.6,
               "Y": 8.29,
               "EY": 8.3,
               "Z": 5.01,
               "EZ": 5.0,
               "DX": 0.02,
               "DY": 0.03,
               "Vol": 5.11,
               "EVol": 5.1,
               "Image": null,
               "UniqueIdentifier": "276b031b-69aa-47de-a087-bf4f1471ff0a",
               "MeasurementName": "R1.1",
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1.1"
             },
             {
               "$type": "CFX.Structures.SolderPasteInspection.SolderPasteMeasurement, CFX",
               "X": 5.62,
               "EX": 5.6,
               "Y": 8.29,
               "EY": 8.3,
               "Z": 5.01,
               "EZ": 5.0,
               "DX": 0.02,
               "DY": 0.03,
               "Vol": 5.11,
               "EVol": 5.1,
               "Image": null,
               "UniqueIdentifier": "49e5f6cf-dd27-4ad7-aa77-469e1da576df",
               "MeasurementName": "R1.2",
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1.1"
             }
           ]
         }
       ]
     }
   ]
}

AOI измерване на отклонения на компоненти:
{
   "TransactionId": "b8c5c639-2ba8-4371-8edb-f743c5a7e33e",
   "InspectionMethod": "SPI",
   "SamplingInformation": {
     "SamplingMethod": "NoSampling",
     "LotSize": null,
     "SampleSize": null
   },
   "Inspector": {
     "OperatorIdentifier": "BADGE489499",
     "ActorType": "Human",
     "LastName": "Smith",
     "FirstName": "Joseph",
     "LoginName": "joseph.smith@abcdrepairs.com"
   },
   "InspectedUnits": [
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 1,
       "OverallResult": "Passed",
       "Inspections": [
         {
           "UniqueIdentifier": "c9b462e5-3e62-482f-9417-268def5bd059",
           "InspectionName": "INSPECT_COMPONENT_OFFSETS",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": [
             {
               "$type": "CFX.Structures.PCBInspection.OffsetMeasurement, CFX",
               "DX": 0.02,
               "DY": 0.01,
               "DZ": 0.01,
               "RXY": 0.01,
               "RZX": 0.15,
               "RZY": 0.15,
               "UniqueIdentifier": "63e2821c-f735-4db9-b355-0b2da6be7040",
               "MeasurementName": null,
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1"
             },
             {
               "$type": "CFX.Structures.PCBInspection.OffsetMeasurement, CFX",
               "DX": 0.02,
               "DY": 0.01,
               "DZ": 0.01,
               "RXY": 0.01,
               "RZX": 0.15,
               "RZY": 0.15,
               "UniqueIdentifier": "dbd43fd9-de85-45c6-92fa-5ff271f9634b",
               "MeasurementName": null,
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R2"
             }
           ]
         }
       ]
     },
     {
       "UnitIdentifier": "PANEL34543535",
       "UnitPositionNumber": 2,
       "OverallResult": "Failed",
       "Inspections": [
         {
           "UniqueIdentifier": "92e9b1c1-e40b-41fb-ad41-74fba7668837",
           "InspectionName": "INSPECT_COMPONENT_OFFSETS",
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": [
             {
               "$type": "CFX.Structures.PCBInspection.OffsetMeasurement, CFX",
               "DX": 0.02,
               "DY": 0.01,
               "DZ": 0.01,
               "RXY": 0.01,
               "RZX": 0.15,
               "RZY": 0.15,
               "UniqueIdentifier": "0c8f1340-1fef-4a32-9ff4-b44521723fe8",
               "MeasurementName": null,
               "TimeRecorded": null,
               "Sequence": 0,
               "Result": "Passed",
               "CRDs": "R1"
             }
           ]
         }
       ]
     }
   ]
}

Пример за резултат от SPI измерване използвайки InspectionMeasurementLean опцията:
{
   "TransactionId": "00000000-0000-0000-0000-000000000000",
   "InspectionMethod": "Human",
   "SamplingInformation": {
     "SamplingMethod": "NoSampling",
     "LotSize": null,
     "SampleSize": null
   },
   "Inspector": {
     "OperatorIdentifier": null,
     "ActorType": "Human",
     "LastName": null,
     "FirstName": null,
     "LoginName": null
   },
   "RecipeName": "SolderRecipeXYZ_TextBoard1",
   "RecipeRevision": "1.3.3.33",
   "InspectedUnits": [
     {
       "UnitIdentifier": "FFSHkkskamJDHS",
       "UnitPositionNumber": 1,
       "OverallResult": "Passed",
       "Inspections": [
         {
           "UniqueIdentifier": "11122344567",
           "InspectionName": null,
           "InspectionStartTime": null,
           "InspectionEndTime": null,
           "TestProcedure": null,
           "Comments": null,
           "Result": "Passed",
           "Verification": "NotVerifiedYet",
           "VerificationDetail": null,
           "Error": null,
           "DefectsFound": [],
           "Symptoms": null,
           "Measurements": [
             {
               "$type": "CFX.Structures.SolderPasteInspection.InspectionMeasurementLean, CFX",
               "X": 0.76,
               "Y": 1.53,
               "Z": 0.086,
               "DX": 0.035,
               "DY": 0.009,
               "Vol": 7.8E-05,
               "A": 1.234,
               "Image": null,
               "UniqueIdentifier": "4fb463d3-1faf-4dd8-9889-1fc49d62b011",
               "MeasurementName": null,
               "TimeRecorded": null,
               "Sequence": 1,
               "Result": "Passed",
               "CRDs": null
             }
           ],
           "RefNo": 1
         }
       ],
       "Verification": "NotVerifiedYet"
     }
   ]
}

Пример за AOI инспекция на панел:
{
   "TransactionId": "436a38e9-fd94-447e-a4d2-db5cc3a4a902",
   "InspectionMethod": "AOI",
   "SamplingInformation": {
     "SamplingMethod": "NoSampling",
     "LotSize": null,
     "SampleSize": null
   },
   "Inspector": {
     "OperatorIdentifier": "BADGE489435",
     "ActorType": "Human",
     "LastName": "Smith",
     "FirstName": "Joseph",
     "LoginName": "joseph.smith@abcdrepairs.com"
   },
   "RecipeName": null,
   "RecipeRevision": null,
   "InspectedUnits": [],
   "InspectedPanel": {
     "UnitIdentifier": "PN123456789",
     "OverallResult": "Passed",
     "PCBVariant": "Variant 1",
     "Inspections": [
       {
         "UniqueIdentifier": "29436eed-f82f-435a-b19c-7b66aa5cf6f6",
         "InspectionName": "INSPECT_F1",
         "InspectionStartTime": null,
         "InspectionEndTime": null,
         "TestProcedure": null,
         "Comments": null,
         "Result": "Passed",
         "Verification": "NotVerifiedYet",
         "VerificationDetail": null,
         "Error": null,
         "DefectsFound": [],
         "Symptoms": [],
         "Measurements": [],
         "RefNo": null
       },
       {
         "UniqueIdentifier": "5fda7d22-1775-4bee-a540-992394f3eccb",
         "InspectionName": "INSPECT_F2",
         "InspectionStartTime": null,
         "InspectionEndTime": null,
         "TestProcedure": null,
         "Comments": null,
         "Result": "Passed",
         "Verification": "NotVerifiedYet",
         "VerificationDetail": null,
         "Error": null,
         "DefectsFound": [],
         "Symptoms": [],
         "Measurements": [],
         "RefNo": null
       }
     ],
     "Verification": "NotVerifiedYet",
     "TotalInspectionCount": 2,
     "Stretch": 1.0,
     "RecognizedStrokeDirection": "forward",
     "Fiducials": [
       {
         "FiducialX": 0.12,
         "FiducialY": 0.16,
         "FiducialRXY": 0.0
       },
       {
         "FiducialX": 0.12,
         "FiducialY": 2.56,
         "FiducialRXY": 0.0
       }
     ]
   }
}
"""

import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class UnitsInspected(CFXMessage):
    """
    Represents a message concerning the inspection of units in a specific system.

    This class extends the base `CFXMessage` class and provides additional
    functionality for initializing and serializing a message with content about
    units inspection. It is intended to facilitate communication by wrapping
    content within a structured XML format. The class utilizes a fixed message
    type identifier to ensure consistency and compatibility.

    Attributes:
    content: Optional[str]
        The content of the message. It defaults to None.

    root: etree.Element
        The root XML element where the serialized content will be appended.

    Parameters:
    content: Optional[str]
        The content of the message to be serialized. Defaults to None.
    """
    MESSAGE_TYPE = "UnitsInspected"

    def __init__(self, content: Optional[str] = None) -> None:
        """
        Represents the initialization of an object that processes a given content and stores it in a serialized format.

        Attributes:
            _content (Optional[str]): The string content to be processed. If no content is provided, it defaults to None.

        Args:
            content (Optional[str]): Represents the content to initialize the object with.
                If not provided, defaults to None.
        """
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
