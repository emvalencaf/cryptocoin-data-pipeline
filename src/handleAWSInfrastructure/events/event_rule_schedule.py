from aws_cdk import aws_events as events
from constructs import Construct


class CdkEventSchedule(Construct):
    def __init__(self, scope: Construct, construct_id: str,
                 custom_rule_name: str, custom_rule_desc: str,
                 custom_rule_schedule: str = "", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        schedule_expression = events.Schedule.expression(custom_rule_schedule) if custom_rule_schedule else events.Schedule.cron(hour="0/12")
        
        self.eventRule = events.Rule(self,
                                     custom_rule_name,
                                     schedule=schedule_expression,
                                     description=custom_rule_desc
                                     )