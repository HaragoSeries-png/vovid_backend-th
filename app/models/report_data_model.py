class DailyReport():
    

    # def __init__(self,txn_date,province,new_case, total_case,new_case_excludebroad,total_case_excluse_broad,new_death,total_death,new_recover,total_recover,update_date):
    #     self.txn_date 
    #     self.province
    #     self.new_case
    #     self.total_case
    #     self.new_case_excludebroad
    #     self.total_case_excluse_broad
    #     self.new_death
    #     self.total_death
    #     self.new_recover
    #     self.total_recover
    #     self.update_date
    def __init__(self,reportJson):
        self.txn_date   = reportJson["txn_date"]
        self.province   = reportJson["province"]
        self.new_case   = reportJson["new_case"]
        self.total_case = reportJson["total_case"]
        self.new_case_excludebroad = reportJson["new_case_excludeabroad"]
        self.total_case_excluse_broad = reportJson["total_case_excludeabroad"]
        self.new_death  = reportJson["new_death"]
        self.total_death = reportJson["total_death"]
        # self.new_recover = reportJson["new_recover"]
        # self.total_recover = reportJson["total_recover"]
        self.update_date = reportJson["update_date"]

    def toString(self):
        return self.txn_date + " have new " + str(self.new_case) + " case "