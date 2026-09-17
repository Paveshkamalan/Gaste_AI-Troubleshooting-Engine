from schema import Action, actionCategory

SAFETY_PRIORITY = {
    actionCategory.auto: 1,
    actionCategory.manual: 2,
    actionCategory.critical: 3
}

def sort_actions(actions: list[Action]) -> list[Action]:
    """Sorts actions safely: auto -> manual -> critical"""
    def get_priority(action: Action):
        cat = action.category
        if not cat:
            return 2 # default to manual
        return SAFETY_PRIORITY.get(cat, 2)
        
    return sorted(actions, key=get_priority)
