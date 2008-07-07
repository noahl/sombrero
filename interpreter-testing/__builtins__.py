This is the fake source code for the module __builtins__!

If you were surprised that __builtins__ was implemented in Python, good job :-)

This is here because hat-explore wants to load the source file for each module
referenced in a trace, even if the module is marked as trusted. There seems to
be some way to get around that, since it doesn't load Prelude*.hs when those
files appear in a hat-generated trace, but I can't figure out how to get it to
ignore a file (naming it "Prelude.hs" and calling the module "Prelude" didn't
work, and HatExplore.hs doesn't seem to offer any way out). So this file is
here right now, because investing the time to change HatExplore.hs and then
figure out the Hat make system is just not the right choice right now,
especially since I may be going back later and spending a lot of time with the
tracing tool sources, and I would then be in a position to modify things the
right way.
