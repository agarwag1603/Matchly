SPACE = ' '
UNDERSCORE = "_"
NEWLINE = '\n'
INFO = "INFO"
ERROR = "ERROR"
DATA_ERROR = f"DataError:{SPACE}"
JD = 'JD'
RESUME = 'RESUME'
CANDIDATE = 'Candidate'
RECRUITER = 'Recruiter'
SEMANTIC_CONFIG = "semantic-config-search"
SEMANTIC_CONFIG_JD = "semantic-config-search-jd"
JD_PROMPT='''Extract the following information from this JD and return JSON with the same names as below:
            - Job Role as JobRole
            - Location, keep only city if city or country if country else None
            - Skills, give this field in a string format
            - Summary of job description as JDSummary
            - Job reference as JobReference
            - Corporate title as CorporateTitle
            - Business Unit as BusinessUnit
            - Business Area as BusinessArea
            - GRCF Role Family as GRCFRoleFamily
            - Business Sector as BusinessSector
            - Business Segment as BusinessSegment
            Note: Strictly, keep as json, do NOT include any markdown formatting such as triple backticks (```), or any extra text. Output should be valid JSON only.
                           
            Job description:'''
 
RESUME_PROMPT='''Extract the following information from this resume and return JSON with the same names as below:
                - Full Name
                - Email
                - Phone
                - Location
                - Skills, give this field in a string format
                - Education(Degree, Institution, Location, GPA, Start Date, End Date)
                - Work Experience(Location, Company, Role, Start Date, End Dates)
                - Certifications with exam id in same line. Output element as "Certifications" as string
                - Certifications Needed Based on skills in same line . Output element only as "Certifications Needed Based on Skills" as string
                - Resume english GrammarCheck Score as "GrammarCheck Score"
                - Flesch Reading Score
                - Section covered and missing score. Consider these section factors : (Work Experience,Education,Skills,
                - Certifications,Project Experience,Objective/Professional Summary,Awards,Volunteer Experience)
                - Return json in this format Section Covered and Missing Score: "Covered": ["Work Experience"],"Missing": ["Objective/Professional Summary"]
                - Profile Summary 2 lines, output variable as Profile Summary
                Note: Strictly, keep as json, do NOT include any markdown formatting such as triple backticks (```), or any extra text. Output should be valid JSON only.
 
                Resume:'''
 