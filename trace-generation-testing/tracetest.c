#include "hat-c.h"

int main(int argc, char **argv)
{
	FileOffset module_Main, variable_main, definition_main, val;
	
	hat_Open("test");
	
	module_Main = mkModule("Main", "test.py", True);
	
	variable_main = mkVariable(module_Main, 1, 3, 0, 0, "main", True);
	
	definition_main = mkConstDef(0, variable_main);
	
	mkConstUse(mkRoot(), 0, definition_main);
	
	entResult(definition_main, 0);
	
	val = mkInt(definition_main, 0, 42);
	
	resResult(definition_main, val, 0);
	
	hat_Close();
	
	return 0;
}
