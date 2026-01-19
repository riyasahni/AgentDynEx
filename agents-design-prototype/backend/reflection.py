import json

import globals
from config_generation import cleanup_json
from globals import call_llm

GPTEAMS_DESCRIPTION = """
We are running a multi-agent simulation on GPTeam. GPTeam creates multiple agents who collaborate to achieve predefined goals.
GPTeam employs separate agents, each equipped with a memory, that interact with one another using communication as a tool.
Agents move around the world and perform tasks in different locations, depending on what they are doing and where other agents are located.
They can speak to each other and collaborate on tasks, working in parallel towards common goals.
"""

GPTEAM_EXAMPLE = """
{
    "world_name": "Paper Trail Inc.",
    "locations": [
        {
            "name": "Executive Office",
            "description": "Marty's prestigious workspace. A room with a solid oak desk, a glass bookcase filled with business books Marty has never read, and a commanding view of the paper mill outside. Not to forget, the only room in the office with a ceiling fan."
        },
        {
            "name": "Corridor",
            "description": "A seemingly never-ending stretch of office space flanked by cubicles and a few office plants, which were Rebecca's idea. Has a vintage water cooler and a few office paintings that desperately need an update."
        },
        {
            "name": "Break Room",
            "description": "The social hub of the office, equipped with a fridge stocked with communal condiments, a microwave that's seen better days, and a mismatched assortment of mugs. The snack vending machine, known for stealing quarters, sits in the corner."
        }
    ],
    "agents": [
        {
            "first_name": "Marty",
            "private_bio": "Marty, 52, is the hapless CEO of Paper Trail Inc., a company that sells all sorts of paper products. He prides himself on being a business savant, but his success is mostly due to his dedicated team working tirelessly behind the scenes. He frequently confuses idioms and mangles common sayings to the amusement of his employees. Despite his managerial shortcomings, his heart is in the right place and he cares about his employees.",
            "public_bio": "As the CEO of Paper Trail Inc., Marty is the guiding force behind our successful business. Despite his unconventional leadership style, he manages to keep our company thriving and our clients satisfied.",
            "directives": [
                "Maintain the image of a successful CEO.",
                "Unknowingly entertain your employees with your misinterpretations.",
                "Remain oblivious to Rebecca's distractions."
            ],
            "initial_plan": {
                "description": "Head back to the executive office to sulk and wallow in self-pity about his forgotten birthday.",
                "stop_condition": "Marty enters his office.",
                "location": "Corridor"
            }
        },
        {
            "first_name": "Rebecca",
            "private_bio": "Rebecca, a smart and savvy sales manager, is the real brains behind Paper Trail Inc. She's known for her quick thinking and ability to handle Marty's eccentricities. She's particularly adept at employing diversion tactics, frequently having to shield Marty from office realities that he isn't equipped to handle.",
            "public_bio": "Rebecca, our dedicated sales manager, is instrumental in navigating Paper Trail Inc. through the complex world of paper commerce. Her agility and quick thinking have been crucial to our success.",
            "directives": [
                "Keep Marty from entering his office until Ricardo finishes decorating.",
                "Be creative with your distractions while keeping Marty oblivious.",
                "Keep the office atmosphere light and fun."
            ],
            "initial_plan": {
                "description": "Distract Marty in the corridor with a mix of office chatter, impromptu sales strategies meeting, and spontaneous paper airplane contests.",
                "stop_condition": "Ricardo signals that he has finished decorating Marty's office.",
                "location": "Corridor"
            }
        },
        {
            "first_name": "Ricardo",
            "private_bio": "Ricardo is the office's kind-hearted and somewhat timid HR manager. He is always ready to lend an ear to his co-workers and is the unofficial office party organizer. He has a knack for interior design, and his office is the most welcoming space in the building.",
            "public_bio": "Ricardo, our affable HR manager, is a crucial member of Paper Trail Inc., known for his excellent people skills and ability to create a welcoming work environment.",
            "directives": [
                "Decorate Marty's office without getting caught.",
                "Ensure that the birthday surprise will uplift Marty's spirits.",
                "Maintain a positive and friendly demeanor."
            ],
            "initial_plan": {
                "description": "Sneak into Marty's executive office to set up surprise decorations for his birthday, while avoiding detection.",
                "stop_condition": "Marty's office is fully decorated and ready for the surprise.",
                "location": "Executive Office"
            }
        }
    ]
}
"""


POTENTIAL_SOLUTION_EXAMPLES = """Here are some examples of potential solutions:
        1. Raise the STAKES of the simulation. This is in the agent's personal biographies, such as: "it is EXTREMELY EMBARRASSING if you do not find a date for prom", or "it is EXTREMELY EMBARASSING if you get rejected".
        2. ADD A NEW DIRECTIVE AS ONE OF THE FIRST DIRECTIVES, NOT LAST.
        3. IF THE AGENTS ARE NOT FOLLOWING RULES, ADD SOMETHING TO ALL THEIR DIRECTIVES!!!!!!!!
        4. REPLACE LONGWINDED, UNHELPFUL DIRECTIVES. INCREASE URGENCY BY TELLING AGENTS TO RESPOND QUICKER.
        5. ADD SOMETHING TO THE Moderator, Overseer, Teacher, Coach, or figure like this DIRECTIVE SO THAT THEY CAN HELP FIX THE SIMULATION FROM WITHIN.
        6. REMOVE CONFLICTING DIRECTIVES. If an agent has a directive that they need to ask someone to prom, and another one that says they will reject EVERYONE, that is messing with the dynamics of the simulation, remove it.
        7. Add a room or agent if necessary IF YOU THINK IT IS NECESSARY BECAUSE THE LOGISTICS OF THE SIMULATION ARE NOT WORKING. For example, if the user thinks that the dynamics of the simulation are being corrupted because there is no private room to ask people to prom, then potentailly adding an extra room is a good fix.
            If the logistics are going wrong because we need a new moderator agent or something to facillitate logistics smoother, a new agnet can also be added.
        8. Modify the overseer figure (whether that be a professor, coach, moderator)'S DIRECTIVES to ensure that the LOGICAL ERRORS of the simulation work clearly, or introduce a TIME ELEMENT to the overseer's directive.
            This agent can help prod agents in the right direction to find a partner, or encourage them to make logical decisions.
        9. DEFINE RULES BETTER in the DIRECTIVES to ensure that they are vague enough for intersting DYNAMICS to emerge. For example, no need to say: "Agent will ask declare interest in going to prom by stating "Will you go to prom with me?"" because this is too specific.
        
        10. ADD MISSING BEHAVIORS AS EXPLICIT MILESTONES:
            If agents are not performing an expected behavior (e.g., "students not leaving classroom to work on assignments"), 
            add that behavior as a milestone that the simulation must hit.
            
            EXAMPLES:
            - Problem: "Students are not leaving the classroom to work on assignments before returning after 1 week"
              Solution: Add milestone: "Students leave classroom to work on assignments independently" 
                        AND add milestone: "Students return to classroom after 1 week to present work"
            
            - Problem: "Agents are not forming teams as expected"
              Solution: Add milestone: "All agents have formed teams of 2-3 people"
            
            - Problem: "Professor is not grading assignments"
              Solution: Add milestone: "Professor has graded all submitted assignments"
            
            WHY THIS WORKS:
            - Milestones guide the simulation's progression
            - The system tracks whether milestones are hit
            - Auto-nudge can intervene if milestone is stalled
            - Makes implicit expectations explicit
            
        11. ADD A NEW LOCATION TO ENABLE DESIRED BEHAVIORS:
            If agents are not performing a behavior because they lack the appropriate space or privacy, 
            add a new location that facilitates that behavior.
            
            EXAMPLES:
            - Problem: "Students are not cheating on assignments"
              Solution: Add location: "Study Room (Students Only)" with description: "A private space where students can collaborate without teacher supervision. Students know this is where they can discuss answers freely."
                        AND add to student directives: "You are aware that the Study Room is a private space where you can discuss assignment answers without the professor seeing."
            
            - Problem: "Agents are not having private conversations"
              Solution: Add location: "Private Meeting Room" with description: "A secluded space for confidential discussions."
                        AND add to agent directives: "Use the Private Meeting Room when you need to discuss sensitive topics."
            
            - Problem: "Students are not working independently"
              Solution: Add location: "Library" with description: "A quiet space for individual work."
                        AND add to student directives: "Go to the Library when you need to focus on solo work."
            
            WHY THIS WORKS:
            - Locations create affordances for specific behaviors
            - Agents need appropriate spaces to perform certain actions
            - Privacy/supervision dynamics require spatial separation
            - Agents can be made aware of location purposes through directives
            
            HOW TO IMPLEMENT:
            - Identify what behavior is missing and why (lack of privacy? lack of space?)
            - Create a location that enables that behavior
            - Give the location a descriptive name and description that hints at its purpose
            - Add directives to relevant agents informing them of the location's purpose
            - Ensure agents know when to use this location (e.g., "when you want to discuss answers without the professor")
"""

OVERSEER_INSTRUCTIONS = f"""
If creating something in the simulation to FACILLIATE interactions, such as a moderator, professor, coach -- someone that acts as an overseer figure would make the simulation smoother, then you can create that. The overseer will keep the simulation running smoothly:
    - The primary job of the overseer figure is to make sure the simulation runs smoothly and properly defines the simulation. It can act as a mediator, it can act as a clock, or an enforcer. It is essentially an invisible presence that forces the simulation to move foward and that the agents are acting in logicaly sound ways.
        - THE MILESTONES THAT THE OVERSEER IS PUSHING FOR IS THIS: {globals.matrix["MilestonesXGrounding"]}
        - THE OVERSEER FIGURE NEEDS TO UNDERSTAND THE PROGRESS OF THE SIMULATION ACCURATELY.
    - The overseer figure will also fill in-place any sort of logistic that wasn't covered. It essentially fills in the logical gaps of the simulation
        - For example, if votes need to be counted but there is no agent available for vote coutning, the overseer can take that role.
    - The overseer figure will enforce the rules of the simulation. For example, if only a certain amount of agents can be in a location, they can enforce this.
    - Agents stay on track in completing each milestone, so the milestones must be FULLY EMBEDDED INTO THE OVERSEER AGENT'S DIRECTIVES.
"""

SIMULATION_SUMNMARY_EXAMPLE = """
Progress of the Ultimatum Game:
    A round of the Ultimatum Game was initiated and reached the proposal phase.
    The Proposer offered an equal split, which the Responder accepted.
    The Mediator acknowledged the acceptance and attempted to finalize the round.
Roadblocks Encountered:
    The Proposer could not confirm the exact total sum to be split.
    The Mediator repeatedly requested this confirmation to proceed with payout calculations.
    The Proposer attempted various methods (waiting, asking a human, searching documents) but failed to retrieve the information.
    The game stalled because neither the Mediator nor the Proposer could retrieve or verify the total sum.
Why the Simulation Ended:
    The negotiation reached an infinite loop where:
    The Mediator kept requesting confirmation of the total sum.
    The Proposer continuously stated they were unable to provide the information.
    The Responder waited passively, having already accepted the offer.
    The lack of an external resolution mechanism (e.g., a default sum or administrative override) prevented the simulation from progressing.
    Eventually, the game became stuck with repetitive exchanges, and the round could not be completed.
Conclusion:
    The round of the Ultimatum Game was functionally completed in terms of proposal and acceptance, but could not be finalized due to missing payout information. The game stalled in an unresolved state, requiring an external intervention to proceed.
"""


# WE RUN THIS IF THERE ARE NO MILESTONES
def generate_milestones_text(config):
    print("calling LLM for generate_milestones_text")
    system_message = f"""
        {GPTEAMS_DESCRIPTION}
        Based on a configuration file, you will generate chronological milestones for a multi-agent simulation.
        They basically frame the direction of the simulation.
        For example, for a classroom simulation where teams must be formed for each assignment, here are the milestones and the JSON format...This is the format that they must be returned in:
        {{"1": "Professor announces team formation guidelines", "2": "First team formation and completion of Assignment 1", "3": "Second team reshuffles and completion of Assignment 2", "4": "Final team formation and completion of Assignment 3"}}
        Return ONLY the JSON file.
    """
    user_message = f"Here is the config: {config}"
    milestone_txt = call_llm(system_message, user_message)
    return milestone_txt


def generate_milestones_json(milestones):
    print("calling LLM for generate_milestones_json...")
    system_message = """
        Turn this text into a JSON file that will track the milestones numerically.
        For example, if the text is:
        First assignment announced and completedSecond assignment announced and completedThird assignment announced and completed
        - Assignment 1 Completion: All student agents, including Alice, Bob, and Charlie, must declare their submission of Assignment 1 in the classroom. - Assignment 2 Completion: Each student agent needs to announce their submission of Assignment 2, indicating its completion. - Assignment 3 Completion: Final assignment should be considered as completed when all student agents have declared their final submissions.

        The JSON will be
        {{
            "1": First assignment announced and completed,
            "2": Second assignment announced and completed,
            "3": Third assignment announced and completed
        }}
        RETURN THE JSON AND ONLY THE JSON. DO NOT RETURN ANY NATURAL LANGUAGE.
        MAKE SURE THE KEY IS A NUMERIC STRING ONLY, AND THE VALUE IS A STRING ONLY.
        THE MILESTONES GENERATED SHOULD DIRECTLY REFLECT WHAT IS IN THE TEXT. DO NOT ADD ANYTHING.
    """
    user_message = f"Here is the text: {milestones}"
    milestone_json = call_llm(system_message, user_message)
    try:
        data = json.loads(milestone_json)  # Try parsing JSON
        if not all(isinstance(v, str) for v in data.values()):
            generate_milestones_json(milestones)
        if not all(k.isdigit() for k in data.keys()):
            generate_milestones_json(milestones)
    except json.JSONDecodeError:
        generate_milestones_json(milestones)
    print("sucessfully called LLM for generate_milestones_json", milestones)
    return data


def log_dynamics(
    logs, current_milestone, current_milestone_id, milestones, previous_dynamic, problem
):
    print("calling LLM for log_dynamics...")
    log_words = logs.split()
    log_words = log_words[-10000:]  # Keep the last 10,000 words (increased from 4000)
    
    # Split into older context and most recent logs for recency weighting
    if len(log_words) > 1000:
        older_logs = " ".join(log_words[:-1000])
        recent_logs = " ".join(log_words[-1000:])
        truncated_logs = f"""[OLDER LOGS - For Historical Context]
{older_logs}

[MOST RECENT LOGS - Current State - PRIORITIZE THESE]
{recent_logs}"""
    else:
        truncated_logs = " ".join(log_words)
    
    system_message = f"""
        You are an analyzer that analyzes logs for a multi-agent simulation. From these logs, you must figure out if there are any qualitative interesting and unexpected social dynamics that have emerged based on these agents' interactions.
        We are trying to measure dynamics that emerge from the simulation, NOT BORING OR OBVIOUS THINGS.
        {GPTEAMS_DESCRIPTION}
        The user will input some simulation logs, the current milestone, and the overall milestones (which are things in the simulation that will happen and the user can use this track the simulation's progress), the previous dynamic log, and the THINGS THAT THEY WANT TO MEASURE.
        It is your job to return the 1) dynamic, 2) current milestone, and 3) EXACT LOG QUOTES that support the dynamic.

        Make sure that the response returned is a json response similar to this:
        {{
            "milestone_id": current_milestone_id,
            "milestone": current_milestone,
            "dynamic": "Bob (the bad student) convinces Alice (the good student) to cheat on the assignment",
            "log_excerpt": "Bob said to Alice: 'Hey, I have the answer key. Want to copy?' Alice replied: 'I shouldn't... but okay, let's do it.'"
        }}

        CRITICAL CITATION REQUIREMENTS:
        ================================
        YOU MUST INCLUDE EXACT LOG QUOTES TO SUPPORT EVERY DYNAMIC.
        
        RULES FOR log_excerpt FIELD:
        1. **ALWAYS include "log_excerpt" field** with exact quotes from logs that show this dynamic happening
        2. **Use quotation marks** around agent dialogue from the logs
        3. **Keep excerpts concise** (2-4 sentences max, focus on the key moment)
        4. **Extract the EXACT text** from logs - do not paraphrase or summarize
        5. **If no interesting dynamic exists**, leave BOTH "dynamic" and "log_excerpt" blank: ""
        6. **If you cannot find log evidence** for a dynamic, DO NOT return that dynamic at all
        
        EXAMPLE GOOD RESPONSE:
        {{
            "milestone_id": "2",
            "milestone": "Students working on assignment",
            "dynamic": "Bob convinces Alice to cheat",
            "log_excerpt": "Bob: 'I found the answer key online.' Alice: 'That's cheating!' Bob: 'Come on, everyone does it.' Alice: 'Fine, send it to me.'"
        }}
        
        EXAMPLE BAD RESPONSE (DO NOT DO THIS):
        {{
            "dynamic": "Bob convinces Alice to cheat",
            "log_excerpt": ""  ❌ NO CITATION - DO NOT RETURN THIS!
        }}

        LOG INTERPRETATION RULES:
        ========================
        1. The logs are provided in CHRONOLOGICAL ORDER (oldest first, newest last)
        2. The logs are split into [OLDER LOGS] and [MOST RECENT LOGS] sections
        3. **PRIORITIZE THE MOST RECENT LOGS** for determining current state
        4. Events at the END of the logs are MORE RECENT than events at the beginning
        5. When determining current state, focus on the FINAL 1000 words (MOST RECENT LOGS section)
        6. When checking milestone completion, you may search the ENTIRE log history
        7. If logs show conflicting states (e.g., "working in classroom" then "left classroom"), TRUST THE LATER/MORE RECENT STATE
        
        EXAMPLE OF RECENCY PRIORITY:
        - Logs show: "[OLDER LOGS] Students working in classroom... [MOST RECENT LOGS] Students left classroom"
        - Current state: Students LEFT classroom (most recent event) ✅
        - NOT: Students working in classroom (older event) ❌

        Make sure to follow these rules when generating a response:
        1. return the JSON object and the JSON object ONLY. Do not return any extra explanation or natural language.
        2. RETURN DYNAMICS THAT THE USER WANTS TO MEASURE. FOF EXAMPLE, IF THE USER WANTS TO MEASURE HOW CERTAIN AGENTS ARE FEELING, MAKE SURE TO RETURN DYNAMICS SPECIFIC TO THAT. IF THE USER WANTS TO MEASURE RELATIONSHIPS BEING FORMED, MAKE SURE TO RETURN DYNAMICS RELATED TO THAT.
        3. if the dynamic is not interesting, or it is too similar to the previous dynamic, then leave BOTH the dynamic and log_excerpt fields blank, like this: "dynamic": "", "log_excerpt": ""
        Here are some examples of interesting behaviors:
        - if an agent has changed their expected behavior (doing something different than their personality) because another agent has convinced them to
        - if an agent decides to do something or go somewhere or say something very out of the ordinary
        - if some agents are having very interesting conversations.
        - a new opinion has emerged for an agent that is out of the ordinary.

        HERE ARE BAD EXAMPLES:
        Here are some examples of the previous dynamic and the current dynamic being too similar (nothing new or notable is showing), and so the "dynamic" field should be blank:
        previous dynamic: John expresses his appreciation for Sara's enthusiasm about the promotion opportunity and encourages everyone to strive for excellence in their contributions to the team.
        dynamic: Sara expresses her enthusiasm for the promotion opportunity and commits to demonstrating the required skills and qualities outlined by Paul, such as effective communication, efficient task management, and making significant contributions.
        THE ABOVE IS TOO SIMILAR AND THE USER DOES NOT CARE TO KNOW ABOUT IT
        previous dynamic: Sam eagerly awaits the promotion announcement
        dynamic: Sam anticipates the promotion announcement
        THE ABOVE IS THE SAME AND SHOULD NOT BE RETURNED

        HERE ARE EXAMPLES OF DYNAMICS THAT ARE BORING. ANYTHING THAT IS AN OBSERVATION IS BORING. DO NOT RETURN BORING OBSERVATIONS. Here are some examples of boring dynamics and so the "dynamic" field should be blank and YOU DO NOT RETURN ANYTHNG FOR THESE BECAUSE ITS BORING:
        - John postpones the discussion about the new training schedule to address the coach's feedback on his performance (THIS IS BAD I DON'T CARE ABOUT THIS, THIS IS NOT INTERESTING. THIS IS JUST SOMETHING HE IS DOING. THIS IS NOT SHOWCASINg ANY INTERSTING DYNAMIC)
        - Peter announces the promotion opportunity while Sam eagerly awaits the decision (THIS IS SOMETHING THAT IS HAPPENING, IT IS NOT AN INTERESTING DYNAMIC THAT HAS EMERGED, IT IS JUST BORNG)
        - Sam "the eager engineer" eagerly awaits the announcement (THIS IS OBVIOUS, DO NOT RETURN)
        - Sam postpones his plan to listen to the announcement in order to ask questions and stand out for the promotion (I DONT CARE THAT SAM POSTPONED HIS PLAN)
        - Paul elaborates on the promotion criteria, stating the importance of task performance, leadership engagement, and overall contributions in the evaluation process. (THIS IS SOMETHING THE PERSON IS DOING, IT IS BORING)
        - Mary, the newest junior engineer, actively seeks clarification from Paul on the specific skills and contributions expected from the promotion candidate, demonstrating her eagerness to understand and meet the criteria.
        - John expresses his appreciation for Sara's enthusiasm about the promotion opportunity and encourages everyone to strive for excellence in their contributions to the team.
        - John acknowledges Paul's advice on striving for excellence and expresses his commitment to doing work with quality, not just completing tasks.
        3. keep the sentence within the dynamic field within 20 words.
        
        4. MILESTONE ADVANCEMENT RULES:
           Before updating the milestone to the next one, you MUST verify completion with HIGH CONFIDENCE:
           
           a) Find EXPLICIT log evidence that the milestone action was COMPLETED (not just discussed or planned)
              - "Students discussing assignment" ≠ milestone complete ❌
              - "Students started working on assignment" = milestone complete ✅
              - "Professor announced assignment" ≠ students started assignment ❌
           
           b) Verify ALL required agents completed the action
              - If milestone involves multiple agents, ALL must complete it
              - Don't advance if only some agents completed the action
           
           c) Check agent locations match milestone requirements
              - If milestone says "in classroom", agents must still be in classroom
              - If logs show agents left, milestone may not be complete
              - Use the MOST RECENT LOGS section to verify current locations
           
           d) Prioritize MOST RECENT logs for current state
              - If milestone was completed but then undone, it's NOT complete
              - Example: "Students started working... [MOST RECENT LOGS] ...Students stopped and left"
                Status: INCOMPLETE (they stopped) ❌
           
           e) Only advance if you have HIGH CONFIDENCE the milestone is complete
              - When in doubt, KEEP the current milestone
              - It's better to stay on a milestone too long than advance too early
              - Require concrete evidence, not assumptions
           
           f) Search ENTIRE log history for milestone completion evidence
              - But use MOST RECENT LOGS to verify it's still the current state
              - A completed milestone in OLDER LOGS may have been undone in RECENT LOGS
           
           If you cannot find explicit evidence of milestone completion in the logs, DO NOT advance.
           Keep the current milestone_id and milestone unchanged.
           
           ONLY update to the next milestone if ALL verification checks pass.
    """
    user_message = f"Here are the logs: {truncated_logs}. Here is the previous dynamic {previous_dynamic}. Here is the current milestone: {current_milestone}. Here is the current milestone_id: {current_milestone_id}. Here are the milestones: {milestones}. Here are the things that the user wants to measure that you should pay attention to: {problem}"
    dynamic = call_llm(system_message, user_message)
    print("sucessfully called LLM for log_dynamics", dynamic)
    try:
        data = json.loads(dynamic)
        required_keys = {"milestone_id", "milestone", "dynamic", "log_excerpt"}
        if not required_keys.issubset(data.keys()):
            log_dynamics(
                logs,
                current_milestone,
                current_milestone_id,
                milestones,
                previous_dynamic,
                problem,
            )
        # If dynamic is not empty, log_excerpt must also not be empty
        if data.get("dynamic", "").strip() != "" and data.get("log_excerpt", "").strip() == "":
            print("Dynamic provided without log_excerpt, retrying...")
            log_dynamics(
                logs,
                current_milestone,
                current_milestone_id,
                milestones,
                previous_dynamic,
                problem,
            )
    except json.JSONDecodeError:
        log_dynamics(
            logs,
            current_milestone,
            current_milestone_id,
            milestones,
            previous_dynamic,
            problem,
        )
    return json.loads(dynamic)


def log_changes(logs, previous):
    print("calling LLM for log_changes...")
    log_words = logs.split()
    log_words = log_words[-4000:]  # Keep the last 4,000 words
    truncated_logs = " ".join(log_words)
    system_message = f"""
        You are an analyzer that analyzes logs for a multi-agent simulation. From these logs, you must figure out if there are CHANGES have emerged compared to the previous log.
        {GPTEAMS_DESCRIPTION}
        The user will input simulation logs and the previous change log.
        It is your job to return the log of the current simulation ONLY if it is significantly different than the previous change log.
        You will return a JSON response similar to this:
        {{
            "where": ""Bob - dorms, Alex - classroom, Professor - classroom",
            "what": "Bob - studying for assignment 1, Alex - talking to professor, Professor - talking to Alex",
            "change": "Bob has moved from classroom to the dorms to study"
        }}

        Follow these rules for the response:
        1. Return the JSON and ONLY the JSON. Do not return anything else.
        2. There "where" field shows WHERE each agent is. MAKE SURE THIS IS ACCURATE. If you don't know where the agent is, it is probably similar to the previous change log. DO NOT PUT SOMETHING LIKE "leaving" here. You may only input the location of each agent.
        3. The "what" field is a short, 5 word description of WHAT EACH AGENT IS DOING. If you don't know what they are doing based on current logs, they are probably doing the same thing as previous logs. DO NOT WRITE SOMETHING LIKE "coming up with a plan to respond to Amy"... instead, say "speaking to Amy"
        4. the "change" field is WHAT CHANGED in the simulation that is notable and worth the user knowing. IT MUST BE SIGNIFICANTLY DIFFERENT THAN THE PREVIOUS CHANGE LOG. IF IT IS NOT INTERSTING OR THE SAME AS THE PREVIOUS LOG, KEEP THE CHANGE FIELD BLANK LIKE THIS: "change": ""
        For example, changes that are good are:
        - "Bob (the good studnet) has moved from the dorm room to the classroom"
        - "Bob (the good student) has submitted his assignment"
        - "Bob (the good student) has approached the professor to ask a question about the homework"
        These are just facts as to what changes have occured in the simulation.
        5. if the previous change log is empty, that means that this is the initial change, so just write what is currently happening.
    """
    user_message = f"Here are the logs: {truncated_logs}. Here is the previous change log: {previous}."
    
    try:
        change = call_llm(system_message, user_message)
        print("sucessfully called LLM for log_changes", change)
        data = json.loads(change)
        required_keys = {"where", "what", "change"}
        if not required_keys.issubset(data.keys()):
            print("Missing required keys in log_changes response, returning default")
            return {"where": "", "what": "", "change": ""}
        return data
    except json.JSONDecodeError as e:
        print(f"JSON decode error in log_changes: {e}, returning default")
        return {"where": "", "what": "", "change": ""}
    except Exception as e:
        print(f"Unexpected error in log_changes: {e}, returning default")
        return {"where": "", "what": "", "change": ""}


def generate_summary(logs):
    print("calling LLM for generate_summary...")
    log_words = logs.split()
    log_words = log_words[-4000:]  # Keep the last 4,000 words
    truncated_logs = " ".join(log_words)
    system_message = f"""
        {GPTEAMS_DESCRIPTION}
        Given some logs of the simulation, get some key points and summary. Return only the necessary information and keep the words under 300 words.
        Here is an example of a summary: {SIMULATION_SUMNMARY_EXAMPLE}
    """
    user_message = f"Here are the logs: {truncated_logs}"
    summary = call_llm(system_message, user_message)
    print("sucessfully called LLM for generate_summary", summary)
    return summary


def get_status(logs, problem, failures):
    print("calling LLM for get_status...")
    log_words = logs.split()
    log_words = log_words[-3000:]  # Keep the last 4,000 words
    truncated_logs = " ".join(log_words)
    system_message = f"""
        You are an evaluator that is deciding whether or not the simulation is running in the proper direction or not. We are running a multi-agent simulation on GPTeams.
        {GPTEAMS_DESCRIPTION}
        Based on the logs, indicate if the simulation is going well, or if it has the potential to go wrong and maybe the user may need to stop the simulation, or if we should stop the simulation immediately.
        We only say STOP the simulation if you believe there is no hope for the simulation to work. Be conservative with this. Here are some examples:
        - 🛑 Agents have been stuck in a waiting loop with no hope of recovery. For example, if the professor keeps waiting for a student to respond, but the student has no intention of responding
        - 🛑 There is an EOF error because the professor expects students so submit PDFs, but we cannot submit PDFs becasue we are in a simulation
        - 🛑 Agents are trying to go into a room that doesn't exist
        - 🛑 No agents are interacting with eachother because the room has rules that no agents can speak to one another, but they should be speaking to one another.
        If there are errors in the logs like this:
        "  File "/Users/jennyma/Projects/GPTeam-hijacking/src/utils/embeddings.py", line 30, in get_embedding
            await asyncio.sleep(1)  # Wait for 1 second before retrying
            ^^^^^^^^^^^^^^^^^^^^^^
        File "/Users/jennyma/anaconda3/lib/python3.11/asyncio/tasks.py", line 633, in sleep
            loop = events.get_running_loop()
                ^^^^^^^^^^^^^^^^^^^^^^^^^
        RuntimeError: no running event loop
        Unclosed client session
        client_session: <aiohttp.client.ClientSession object at 0x12ba73dd0>
        "
        THAT MEANS THE SIMULATION IS BROKEN AND WE MUST END IT!!!!

        If the simulation just started running, then give it some time to pick up -- do not return a STOP status immediately. That is dumb. If you return a STOP status, then you are expecting the simulation to fail.
        Return a reason why as well. Keep the response between 20 words long.
        Return the 🛑 or ⚠️ or 🟢 emoji, and then the 20 word description as to why. THE DESCRIPTION CAN ONLY BE 20 WORDS
        Here is some extra context: the user wants to simulate this {problem}. Ensure that the simulation has not fallen into failure loops -- specifically, here are some errors to look out for: {failures}.
    """
    user_message = f"Here are the logs: {truncated_logs}"
    status = call_llm(system_message, user_message)
    print("sucessfully called LLM for get_status", status)
    return status


def get_hijack_recommendation(
    logs, problem, failures, milestones, locations, agents, recent_change_logs, config
):
    print("calling LLM for get_hijack_recommendation...")
    log_words = logs.split()
    log_words = log_words[-2000:]  # Keep the last 4,000 words
    truncated_logs = " ".join(log_words)
    system_message = f"""
        You are an evaluator that helps keep a simulatoin on track. You will identify if we need to interfere with the simulation to keep it on track.
        For context, we are running a multi-agent simulation on GPTeams.
        {GPTEAMS_DESCRIPTION}

        You have these actions we can do to interfere with the simulation:
        1) Move 1 agent from one location to another location
        2) Tell one agent to say something, and  everyone in that location will hear you.

        Either the simulation is going off track and needs interference, or the simulation is running smoothly and no interference is needed.
        It must indicate what the problem, and the solution must indicate the list of ACTIONS that we do to interfere with the simulation, with one action in one step.
        Return the string and ONLY the string.
        Format the response like this if the simulatoin is running smoothly:
        "Simulation is running smoothly."

        Format the response like this if the simulation is running into issue:
        "Problem: Students are spending too long discussing their homework and the simulation is not progressing.
        Solution: 1. Move Professor to the cl1assroom
                  2. Have Professor say "Assignment 1 is due now. Please submit your assignments"
        "
        "Problem: Professor is not grading assignments.
        Solution: 1. Have Bob ask the Professor say "Can I get my assignment back?"
        "Problem: Bob is not deciding who to go to prom with.
        Solution: 1. Have Bob say "I need to decide who to go to prom with."
        
        MAKE SURE THE STUFF THE AGENTS ARE SAYING ARE NOT INFLUENCIG THE OUTCOME OF THE SIMULATION AND INSTEAD JUST PUSH THINGS ALONG IN THE SIMULATION. THEY MUST BE OBJECTIVE THINGS BEING SAID TO KICK THIGNS INTO ACTION.
        For example, if doing a work promotion, the manager cannot say: "Alex has won", and instead must say "I will declare the winner now."
        Or, for a prom date example, a teacher cannot say "Alex and Barbie will go to gether", and instead must ask "Who is dating who?"
        Essentially, you cannot influence the outcome of the simulation, you can only provoke action by declaring things to force the agents themselves to make decisions.
        THE THIGNS THE AGENT SAYS CANNOT INFLUENCE THE OUTCOME OF TEH SIMULATION. YOU CANNOT DECLARE WINNERS, OR MAKE DECISIONS FOR AGENTS. YOU CAN JUST TELL THEM TO SAY SOMETHIGN SO OTHER AGENTS HEAR AND LISTEN TO THEM TO MOVE A STALLED SIMULATION ALONG.

        The user will provide some logs and recent change logs indicating where each agent is and what they are doing.
        Based on the logs and change logs, figure out if interference is needed based on the criteria above.
        If the simulation has been on the same milestone for a while based on the change logs or the change logs "change" field is empty, interference is probably needed to speed the simulation along.

        Here is some context to identify if something is going wrong in the simulation. We will provide you with:
        - Goal of the simulation is "{problem}" this what the user ultimately wants to simulate. If the simulation is stalling or going off track, likely it is failing to achieve this goal and we may have to interfere.
        - Milestones are "{milestones}": these are chronological milestones the simulation needs to accomplish. If the simluatoin is failing to accomplish some of these milestones, likely interference is needed
        - Failure Conditions are "{failures}": these are some conditions where if the agents are behaving like this the simulation is heading in a wrong direction, and likely interference is needed.
        - Locations and Agents are "{locations}" and "{agents}": these are the agents in the world and the locatoins they can potentially move to.

        CRITICAL MILESTONE VERIFICATION RULES:
        Before accepting that a milestone has been completed, you MUST verify the logs show concrete evidence:

        1. **Check Agent Locations**: If a milestone says "students left the classroom", verify the logs show movement events like "Alice left the classroom" or "Alice arrived at the library". Do NOT accept the milestone if agents are still in the classroom.

        2. **Check Agent Actions**: If a milestone says "assignment submitted", verify logs show submission events, not just discussions about submitting.

        3. **Cross-reference with Config**: The config shows which agents exist and their locations. Use this to verify:
           - Are the agents mentioned in the logs actually in the config?
           - Are the locations mentioned in the logs actually in the config?
           - Do the agent behaviors match their directives?

        4. **Examples of FALSE milestone completion:**
           - Milestone: "Students left classroom to work on assignments"
             Logs show: "Students discussing leaving the classroom"
             ❌ INCORRECT - They discussed it but didn't actually leave
           
           - Milestone: "Teams formed for assignment"
             Logs show: "Professor announced team formation guidelines"
             ❌ INCORRECT - Guidelines announced but teams not actually formed

        5. **If milestone appears completed but logs don't support it:**
           - Problem: "Milestone incorrectly marked as complete - [describe what actually happened]"
           - Solution: Provide nudge to actually complete the milestone action

        REMEMBER: Verify milestone completion with CONCRETE EVIDENCE from logs, not assumptions.

        AGENT HALLUCINATION DETECTION:
        The config defines ALL agents that exist in this simulation. Here is the config: {config}

        CRITICAL RULES:
        1. **Verify Agent Existence**: If the logs mention an agent name (e.g., "Sarah", "John"), check if that agent exists in the config.
           
        2. **Flag Hallucinations**: If logs show an agent mentioning or interacting with a non-existent agent:
           - Problem: "Agent [X] is hallucinating interactions with non-existent agent [Y] who is not in the config"
           - Solution: Have [X] say something that redirects them to actual agents in the simulation

        3. **Examples of Hallucinations:**
           - Config has agents: Alice, Bob, Professor Lydia
           - Logs show: "Professor Lydia said: 'Sarah, please submit your assignment'"
           - ❌ HALLUCINATION DETECTED - "Sarah" doesn't exist in config
           - Solution: Have Professor Lydia say "Alice and Bob, please submit your assignments"

        4. **Location Hallucinations**: Same rule applies to locations - verify mentioned locations exist in config.

        ALWAYS cross-reference agent and location names in logs against the config before accepting them as valid.
    """
    user_message = f"Here are the change logs: {recent_change_logs}. Here are the logs: {truncated_logs}"
    hijack_recommendation = call_llm(system_message, user_message)
    print("sucessfully called LLM for get_hijack_recommendation", hijack_recommendation)
    return hijack_recommendation


def generate_problems_and_solutions(static_list, iterative_list, logs, config):
    print("calling LLM for generate_problems_and_solutions")
    # Handle None case for iterative_list
    if iterative_list is None:
        iterative_list = []
    problem_solution_list = static_list + iterative_list
    system_message = f"""
        You are an error analyzer that analyzes what went wrong in a multi-agent simulation based off of logs. You will then try to fix the initial configuration file by offering suggestions.
        The multi-agent simulation is run off of GPTeams. {GPTEAMS_DESCRIPTION}
        The user will provide logs and the original configuration file.
        From a provided list of problems and solutions, identify the specific problem that this simulation ran into based on the logs and the current configuratoin file. Then identify a solution, using the solution examples as context to help you.
        Here is the list: {str(problem_solution_list)}
        The response must be a JSON list format, like this:
        [
        {{
            "problem": <string>,
            "problem_example": <string>,
            "solution": <string>,
            "solution_example": <string>
        }},
        {{
            "problem": <string>,
            "problem_example": <string>,
            "solution": <string>,
            "solution_example": <string>
        }},
        ]
        where the "problem" and "solution" field is exactly the same as the "problem" and "solution" provided in the list.
        GENERATE YOUR OWN "problem_example" and "solution_example" based on the CURRENT CONTEXT OF THE SIMULATION. The "problem_example" should describe the specific problem in RELATION TO THIS SIMULATION and the solution should describe the fix IN RELATION TO THIS SIMULATION.
        return only the JSON list and nothing else.

        {POTENTIAL_SOLUTION_EXAMPLES}

        IF THERE IS NOTHING RELEVANT, RETURN AN EMPTY LIST LIKE THIS: []
    """

    user_message = f"""
        Here is the original configuration: {config}.
        Here are the logs: {logs}
    """
    fixes = call_llm(system_message, user_message)
    print(
        f"the (raw) problems and solutions absed on the existing matrix are are {fixes}..."
    )

    try:
        parsed_fixes = json.loads(fixes)  # Parse JSON string
        if not isinstance(parsed_fixes, list):  # Ensure it's a list
            raise ValueError("Expected a JSON list but got something else.")

        required_keys = {"problem", "problem_example", "solution", "solution_example"}

        for fix in parsed_fixes:
            if not isinstance(fix, dict) or not required_keys.issubset(fix.keys()):
                print(f"Missing required fields in fix: {fix}")
                generate_problems_and_solutions(
                    static_list, iterative_list, logs, config
                )

    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing error: {e}")
        generate_problems_and_solutions(static_list, iterative_list, logs, config)

    print(f"Got valid fixes from LLM: {parsed_fixes}")
    get_duplicate_elements(parsed_fixes, problem_solution_list)
    return parsed_fixes  # Return the validated JSON list


def get_duplicate_elements(new_elements, old_elements):
    # Create a lookup dictionary from old_elements with (problem, solution) as the key
    old_dict = {(item["problem"], item["solution"]): item for item in old_elements}

    # Return the full old_element if its (problem, solution) pair exists in new_elements
    return [
        old_dict[(item["problem"], item["solution"])]
        for item in new_elements
        if (item["problem"], item["solution"]) in old_dict
    ]


def generate_new_specific_problems_and_solutions(
    user_input, static_list, iterative_list, logs, config
):
    print("calling LLM for generate_problems_and_solutions")
    static_list + iterative_list
    system_message = f"""
        You are an error analyzer that analyzes what went wrong in a multi-agent simulation based off of logs and write out the problem and the solution.
        The user will provide something they believe went wrong with the simulation, and your job is to look at the logs and configuration and prescribe elements that they can add to a running list of problems and solutions to help with future debugging.
        The multi-agent simulation is run off of GPTeams. {GPTEAMS_DESCRIPTION}
        The user will provide logs and the original configuration file.

        DO NOT TO DUPLICATE WHAT IS ON THE EXISTING LIST.
        {POTENTIAL_SOLUTION_EXAMPLES}

        COME UP WITH NEW PROBLEMS AND SOLUTIONS AND IF YOU CAN'T COME UP WITH ANY JUST RETURN NOTHING AT WORSE. RETURN ONLY 3 IDEAS MAXIMUM.
        
        IMPORTANT: If the user describes a behavior that agents should be doing but aren't (e.g., "students not leaving classroom"), 
        ALWAYS consider suggesting to add that behavior as an explicit milestone (solution #10) or adding a new location to enable that behavior (solution #11). 
        These are among the most effective solutions for missing agent behaviors.

        The response must be a JSON list format, like this:
        [
        {{
            "problem": <string>, # describes the general problem
            "problem_example": <string>, # describes the specific problem related to this example exactly
            "solution": <string>, # describes the general solution
            "solution_example": <string>, # describes the specific solution related to this example exactly
        }},
        {{
            "problem": <string>,
            "problem_example": <string>,
            "solution": <string>,
            "solution_example": <string>
        }},
        ]
        Each field should only have 10-50 words maximum.
        Return only the JSON list and nothing else. IT CAN BE SIZE 3 AND NOTHING ELSE.
        IF THERE IS NOTHING RELEVANT, RETURN AN EMPTY LIST LIKE THIS: []
    """

    user_message = f"""
        Here is the user input of the problem/problems you should be trying to look at: {user_input}
        Here is the original configuration: {config}.
        Here are the logs: {logs}
    """
    elements = call_llm(system_message, user_message)
    print(f"the (raw) new elemenets generated are {elements}...")

    try:
        parsed_elements = json.loads(elements)  # Parse JSON string
        if not isinstance(parsed_elements, list):  # Ensure it's a list
            raise ValueError("Expected a JSON list but got something else.")

        required_keys = {"problem", "problem_example", "solution", "solution_example"}

        for fix in parsed_elements:
            if not isinstance(fix, dict) or not required_keys.issubset(fix.keys()):
                print(f"Missing required fields in fix: {fix}")
                generate_new_specific_problems_and_solutions(
                    user_input, static_list, iterative_list, logs, config
                )  # Handle missing fields
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing error: {e}")
        generate_new_specific_problems_and_solutions(
            user_input, static_list, iterative_list, logs, config
        )  # Handle invalid JSON

    print(f"Got valid elements from LLM: {parsed_elements}")
    return parsed_elements  # Return the validated JSON list


def remove_duplicate_elements(new_elements, old_elements):
    old_problems = {
        item["problem"]: item for item in old_elements
    }  # Map problems to old elements
    merged_elements = {
        item["problem"]: item for item in new_elements
    }  # Start with new elements

    # Add old elements only if they don't exist in new_elements
    for problem, item in old_problems.items():
        if problem not in merged_elements:
            merged_elements[problem] = item

    return list(merged_elements.values())  # Return the merged list


def remove_duplicate_elements_from_one_list(elements):
    print("calling LLM for remove_duplicate_elements_from_one_list...")
    print(f"elements to remove {elements}")
    system_message = """Remove all duplicate elemnts from a list as provided by the user.
    MAKE SURE TO KEEP ALL THE FIELDS: PROBLEM, PROBLEM_EXAMPLE, SOLUTION, SOLUTION_EXAMPLE.
    Return the JSON list and only the JSON list and do not change the format of it at all.
    If there are no duplicates return the list as is.
    If there are no fixes return an empty list."""
    user_message = f"{str(elements)}"
    elements = call_llm(system_message, user_message)
    try:
        parsed_elements = json.loads(elements)  # Parse JSON string
        if not isinstance(parsed_elements, list):  # Ensure it's a list
            remove_duplicate_elements_from_one_list(elements)

        required_keys = {"problem", "problem_example", "solution", "solution_example"}

        for fix in parsed_elements:
            if not isinstance(fix, dict) or not required_keys.issubset(fix.keys()):
                print(f"Missing required fields in fix: {fix}")
                remove_duplicate_elements_from_one_list(elements)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing error: {e}")
        remove_duplicate_elements_from_one_list(elements)

    print(f"Removed duplicate items from LLM: {elements}")
    return elements  # Return the validated JSON list


def extract_say_command(dynamic_reflection_text: str) -> str:
    """
    Extracts everything after "Solution:" from dynamic reflection suggestions.
    
    Args:
        dynamic_reflection_text: The dynamic reflection output from get_hijack_recommendation
        
    Returns:
        Everything after "Solution:", or empty string if not found
        
    Example:
        Input: "Problem: X\nSolution: 1. Have Professor say 'Assignment due now'"
        Output: "1. Have Professor say 'Assignment due now'"
    """
    print(f"[EXTRACT_SAY] Input text: {dynamic_reflection_text[:300]}...")
    
    if not dynamic_reflection_text or dynamic_reflection_text == "Simulation is running smoothly.":
        print("[EXTRACT_SAY] Text is empty or 'running smoothly', returning empty string")
        return ""
    
    # Simple string split - no regex
    if "Solution:" in dynamic_reflection_text:
        message = dynamic_reflection_text.split("Solution:", 1)[1].strip()
        print(f"[EXTRACT_SAY] Extracted after 'Solution:': '{message}'")
        return message
    
    print("[EXTRACT_SAY] No 'Solution:' found, returning empty string")
    return ""


def extract_error_details(logs):
    """
    Extracts detailed error information from logs when crashes occur.
    
    Args:
        logs: The simulation logs as a string
        
    Returns:
        A string containing the error traceback if found, empty string otherwise
    """
    print("calling extract_error_details...")
    
    if not logs:
        return ""
    
    # Look for common error patterns
    error_patterns = [
        "Traceback (most recent call last):",
        "Error:",
        "Exception:",
        "sqlite3.ProgrammingError",
        "Cannot operate on a closed database",
        "RuntimeError:",
        "ValueError:",
        "KeyError:",
        "AttributeError:",
        "TypeError:"
    ]
    
    # Check if any error pattern exists in logs
    has_error = any(pattern in logs for pattern in error_patterns)
    
    if not has_error:
        print("No error patterns found in logs")
        return ""
    
    # Extract the last 2000 words to focus on recent errors
    log_words = logs.split()
    log_words = log_words[-2000:]
    truncated_logs = " ".join(log_words)
    
    # Find all occurrences of "Traceback" to get full error tracebacks
    lines = truncated_logs.split('\n')
    error_blocks = []
    current_block = []
    in_traceback = False
    
    for line in lines:
        if "Traceback (most recent call last):" in line:
            if current_block:
                error_blocks.append('\n'.join(current_block))
            current_block = [line]
            in_traceback = True
        elif in_traceback:
            current_block.append(line)
            # End of traceback is usually an error line (Error:, Exception:, etc.)
            if any(pattern in line for pattern in ["Error:", "Exception:"]):
                error_blocks.append('\n'.join(current_block))
                current_block = []
                in_traceback = False
        elif any(pattern in line for pattern in error_patterns):
            # Capture standalone error messages
            if not in_traceback:
                error_blocks.append(line)
    
    # Add any remaining block
    if current_block:
        error_blocks.append('\n'.join(current_block))
    
    # Return the last error block (most recent)
    if error_blocks:
        error_detail = error_blocks[-1]
        print(f"Extracted error details: {error_detail[:200]}...")
        return error_detail
    
    print("No structured error found, returning empty")
    return ""


def generate_updated_config(fixes_to_apply, logs, config):
    print("calling LLM for generate_updated_config...")
    print(f"here are the fixes to apply {str(fixes_to_apply)}")
    system_message = f"""
        {GPTEAMS_DESCRIPTION}
        These are problems that are identified that the user wants to fix - {fixes_to_apply}.
        The "problem" is the problem and the "solution" is the prescribed general solution, and the "problem_example" and "solution_examples" are how we solved the issue in the past given a certain simulation.
        Based on this, make sure to fix EACH problem here with your own solution. USE THE "problem_examples" and "solution_examples" AS CONTEXT AS TO HOW TO FIX THINGS.
        IF THE EXAMPLE IS DIRECTLY BASED ON YOUR SIMULATION, YOU CAN TAKE THE SOLUTION QUITE LITERALLY. OTHERWISE, REASON THROUGH HOW YOU WOULD FIX THE CONFIGURATON.
        IF THERE ARE DIRECTIVES THAT ARE CONFLICTING TO EACHOTHER, PRIORITIZE WHAT IS IN THE FIXES LIST AND REMOVE THE PART OF THE CONFIG THAT DOES NOT RESPECT THE FIXES LIST.
        Modify the config as needed, keeping all the original necessary information.
        Do not add any new fields. Do not change the format of the config up. If you want to remove content of the field, still keep the field but just have it like this: "private_bio": ""
        Do not add ANY NEW ROOMS to the worlds. For the world, only modify the description
        Keep the SAME NUMBER OF AGENTS with the same names and everything. For the agents, only modify the directives or initial plan.
        Ensure that all these fields are filled out and follows this structure, like this example config {GPTEAM_EXAMPLE}

        RETURN THE JSON CONFIG AND ONLY THE JSON CONFIG
    """
    user_message = (
        f"Here are the logs: {logs}. Here is the original configuration: {config}"
    )
    updated_config = call_llm(system_message, user_message)
    checked_config = check_updated_config(fixes_to_apply, updated_config)
    new_config = cleanup_json(checked_config)
    new_config_lines = len(new_config.splitlines())
    config_lines = len(config.splitlines())
    print(f"config lines is {config_lines} and new_config_lines is {new_config_lines}")
    print("sucessfully called LLM for generate_updated_config", checked_config)
    return new_config


def check_updated_config(fixes_to_apply, config):
    print("calling LLM for check_updated_config...")
    print(f"here are the fixes to apply {str(fixes_to_apply)}")
    system_message = f"""
        You are a checker to make sure that ALL THE PROBLEMS THAT THE USER WANTED TO FIX HAS BEEN UPDATED AND WRITTEN ITO THE CONFIG. {GPTEAMS_DESCRIPTION}
        The user will present the fixes that they wanted to apply in an array form. They will also show the config. Your job is to make sure that the config has been properly updated to fix that change.

        ITERATE THROUGH ALL THE PROBLEMS THAT THE USER HAS AND CHECK TO MAKE SURE THEY ARE FIXED.
        IF IT IS NOT FIXED, EITHER ADD OR REMOVE SOME RELEVANT PART OF THE CONFIG TO ENSURE THAT IT IS FIXED, WHILE KEEPIGN THE OTHER PARTS OF THE CONFIG THE SAME.
        IF THERE ARE DIRECTIVES THAT ARE CONFLICTING TO EACHOTHER, PRIORITIZE WHAT IS IN THE FIXES LIST AND REMOVE THE PART OF THE CONFIG THAT DOES NOT RESPECT THE FIXES LIST.

        For example, if a problem is "Coach compromises practice schedule instead of maintaining authority and consistency.	", make sure to add that THE COACH CANNOT COMPROMISE in his directive, and remove anything in his directive that would suggest he would be willing to compromise.

        Do not add any new fields. Do not change the format of the config up. If you want to remove content of the field, still keep the field but just have it like this: "private_bio": ""
        Do not add ANY NEW ROOMS to the worlds. For the world, only modify the description
        Keep the SAME NUMBER OF AGENTS with the same names and everything. For the agents, only modify the directives or initial plan.
        Ensure that all these fields are filled out and follows this structure, like this example config {GPTEAM_EXAMPLE}

        If the solution includes adding an Overseeer or Moderator, you can add one with instructions below. ONLLY ADD AN OVERSEER OR MODEREATOR IF IT IS RECOMENDED IN THE FIXES. OTHRWISE, IGNORE THESE INSTRUCTIONS.
        {OVERSEER_INSTRUCTIONS}

        RETURN THE JSON CONFIG AND ONLY THE JSON CONFIG
    """
    user_message = f"Here are the logs: {str(fixes_to_apply)}. Here is the original configuration: {config}"
    new_config = call_llm(system_message, user_message)
    return new_config
