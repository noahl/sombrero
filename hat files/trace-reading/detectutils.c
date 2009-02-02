/*
 *  Utility functions for hat-detect.
 */

/* -- This file is a section of the larger detectutils.c found in the hat-2.05
 *    source tree. Taken July 10th, 2008 -- Noah Lavine */

#include <stdio.h>
#include <errno.h>
#include <string.h>

#ifdef DEBUG
#define HIDE(x) x
#else
#define HIDE(x)
#endif

#include "detectutils.h"

/* Print a message to stderr if the asserted condition is violated. */
void
assert (Bool cond, char *act)
{
  if (!cond) {
    fprintf(stderr,"Assertion failed: %s at 0x%x\n",act,q_position);
  }
}

/* Look for the file node that corresponds to the definition of Main.main */
FileOffset
findMainUse (Bool findUse)
{
    FileOffset fo;
    FileOffset atom;
    FileOffset def;
    FileOffset use;
    char c;
    char *str;
    
    // We should find the main module at 0x10
    fseek(HatFileSeq,0x10,SEEK_SET); q_position=0x10;
    q_fread(&c,sizeof(char),1,HatFileSeq);
    assert (lower5(c)==Module, "Module tag");
    str = q_readString();
    assert (!strcmp(str,"Main"),"Module is Main");
    
    // The next thing shoult be the atom variable belonging to that module
    q_readString();
    atom = q_position;
    q_fread(&c,sizeof(char),1,HatFileSeq);
    assert (lower5(c)==AtomVariable, "AtomVariable tag");
    fo = q_readFO();
    assert (fo==0x10, "AtomVariable module is Main");
    
    {	/* skip defnpos */
        int x;
        q_fread(&x,sizeof(int),1,HatFileSeq);
    }
    {	/* skip defnpos */
        int x;
        q_fread(&x,sizeof(int),1,HatFileSeq);
    }
    {	/* skip fixity */
        char x;
        q_fread(&x,sizeof(char),1,HatFileSeq);
    }
    
    // Main takes no arguments
    q_fread(&c,sizeof(char),1,HatFileSeq);
    assert (c==0, "AtomVariable has arity 0");
    
    // Make sure the deffinition is main
    str = q_readString();
    assert (!strcmp(str,"main"),"AtomVariable is main");
    
    // Make sure there is a constant definition pointing at main
    def = q_position;
    q_fread(&c,sizeof(char),1,HatFileSeq);
    assert (lower5(c)==ExpConstDef, "ExpConstDef tag");
    q_readFO(); q_readFO();
    fo = q_readFO();
    assert (fo==atom, "ExpConstDef points to AtomVariable main");
    
    // Make sure that main is called
    use = q_position;
    q_fread(&c,sizeof(char),1,HatFileSeq);
    assert (lower5(c)==ExpConstUse, "ExpConstUse tag");
    if (hasSrcPos(c)) q_readFO();
    q_readFO();
    fo = q_readFO();
    assert(fo==def, "ExpConstUse points to ExpConstDef");
    
    if (findUse)
    {
        return use;
    }
    else
    {
        return def;
    }
    
    /* postcondition: q_position points to first node following ExpConstUse */
}
