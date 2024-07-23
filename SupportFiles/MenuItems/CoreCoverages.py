import logging
from SupportFiles.MultiLog import MultiLog
from SupportFiles.Timing import Timing
from SupportFiles.Actions import Actions


class CoreCoverages:
    core_coverages_time = Timing()
    coverage_a = 300000
    coverage_c = coverage_a
    browser = None

    core_values = ["Risk.ListOfTenantsAndOccupancy", "Risk.BasementInd", "Risk.BldgCentralHeatInd", "Risk.CircuitBreakerProtInd", "Risk.UndergradResidentInd",
                   "Risk.SpaceHeatersInd", "Risk.FrameClearance15ftInd", "Risk.ShortTermRent", "Risk.MercantileOfficeOccupantsInd", "Risk.ExcessLinesInd"]

    core_values_after = ["Risk.RoofUpdatedIn15YrsInd", "Risk.AdequateSmokeDetInd",
                         "Risk.BldgOccGt75PctInd", "Risk.EgressFromAllUnitsInd", "Risk.MaintProgramInd"]

    def __init__(self, browser):
        self.browser = browser

    def start_coverages(self):
        self.core_coverages_time.start()

        MultiLog.add_log(f"Starting Core Coverages", logging.INFO)

        self.browser.execute_script(
            "document.getElementById('Wizard_Risks').click();")

        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(
            self.browser, "Building.ConstructionCd", "Frame")
        Actions.check_for_value(self.browser, "Building.YearBuilt", keys=2020)
        Actions.check_for_value(self.browser, "Building.OccupancyCd",
                                "Owner occupied dwelling")
        Actions.check_for_value(self.browser, "Building.Seasonal", "No")
        Actions.check_for_value(self.browser, "Risk.TypeCd", "DP2")
        Actions.check_for_value(
            self.browser, "Building.BuildingLimit", keys=300000)
        Actions.check_for_value(self.browser, "Building.NumOfFamilies", "1")
        Actions.check_for_value(
            self.browser, "Building.OccupancyCd", "Primary Residence")
        Actions.check_for_value(self.browser, "Building.CovALimit",
                                keys=self.coverage_a)
        Actions.check_for_value(
            self.browser, "Building.NumOfFamiliesSameFire", "Less Than 5", False, None)
        Actions.check_for_value(
            self.browser, "Building.FuelLiability", "300000")
        Actions.check_for_value(
            self.browser, "Building.OilTankLocation", "none")
        Actions.check_for_value(self.browser, "Building.CovELimit", "300000")
        Actions.check_for_value(self.browser, "Building.CovFLimit", "2000")
        Actions.check_for_value(self.browser, "Building.CovCLimit",
                                keys=self.coverage_c)
        Actions.check_for_value(self.browser, "Building.StandardDed", "1000")
        Actions.check_for_value(self.browser, "Building.TerritoryCd", keys="1")
        Actions.check_for_value(self.browser, "Risk.WorkersCompInd", "100000")
        Actions.check_for_value(
            self.browser, "Risk.WorkersCompEmployees", "none")
        Actions.check_for_value(
            self.browser, "Building.HurricaneMitigation", "No Action")
        Actions.check_for_value(
            self.browser, "Building.BuildingClassDescription", "75% or more Apartments")
        Actions.check_for_value(
            self.browser, "Building.BuildingClassDescription", "67% or more Apartments")
        Actions.check_for_value(
            self.browser, "Building.ContentClassDescription", "None - Building Owner only")
        Actions.check_for_value(
            self.browser, "Building.BuildingLimit", keys=900000)
        Actions.check_for_value(
            self.browser, "Building.DistanceToHydrant", "1000")
        Actions.check_for_value(self.browser, "Risk.SqFtArea", keys=2000)
        Actions.check_for_value(
            self.browser, "Risk.PremisesAlarm", "None", True)
        Actions.check_for_value(
            self.browser, "Risk.YrsInBusinessInd", "1", True)
        Actions.check_for_value(
            self.browser, "Building.NumOfApartmentCondoBuilding", keys=5)
        Actions.check_for_value(
            self.browser, "Building.MaxNumOfAptCondoBetweenBrickWalls", keys=5)
        Actions.check_for_value(self.browser, "Building.NumOfStories", keys=5)
        Actions.check_for_value(
            self.browser, "Risk.ListOfTenantsAndOccupancy", keys="None")
        Actions.check_for_value(self.browser, "Risk.NumOfStories", keys=3)
        Actions.check_for_value(
            self.browser, "Building.ProtectionClass", keys=3)

        # if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
        for value in self.core_values:
            Actions.check_for_value(self.browser, value, "No", False)

        # save(self.browser)
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)

        for value in self.core_values_after:
            Actions.check_for_value(self.browser, value, "No", False)

        try:
            t = Actions.find_Element(
                self.browser, "MissingFieldError").is_displayed()
            if t:
                MultiLog.add_log(
                    f"Core Coverages Was not able to Complete", logging.ERROR)
        except:
            MultiLog.add_log(
                f"Finishing Core Coverages without Errors", logging.INFO)
            self.core_coverages_time.end()
            MultiLog.add_log(f"Time to complete Core Coverages: {
                             self.core_coverages_time.compute_time()} seconds", logging.INFO)

        # click the save button
        Actions.save(self.browser)
