/* Primitive functions for writing the ART trace
 * Control C interruption not yet implemented
 * highest bit of fileoffset is used to mark those pointing to hidden nodes */

#define HIDE(x) PRINT_IF_DEBUGGING(x)

#define HeaderSize (8 + 2*sizeof(FileOffset))
typedef char byte;

/* Write trace nodes */

FileOffset
mkModule(char *modname, char *srcfile, Bool traced)
{
  FileOffset fo;

  fo = writeTag(Module | (traced?TracedModule:0)
               ,1+stringSize(modname)+stringSize(srcfile));
  writeString(modname);
  writeString(srcfile);
  HIDE(fprintf(stderr,"\tmkModule %s (%s) -> 0x%x\n",modname,srcfile,fo);)
  return fo;
}

FileOffset
mkSrcPos(FileOffset moduleTraceInfo,int begin,int end)
{
  FileOffset fo;

  fo = writeTag(SrcPos,1+sizeof(FileOffset)+2*sizeof(int));
  writeFileOffset(moduleTraceInfo);
  writeInt(begin);
  writeInt(end);
  HIDE(fprintf(stderr,"\tmkSrcPos %d %d -> 0x%x\n",begin,end,fo);)
  return fo;
}


/* Exp nodes; if use is 0, then the variant without a use field is written */

FileOffset
mkResApp1(FileOffset parent,FileOffset use,FileOffset fun
         ,FileOffset arg1)
{
  FileOffset fo;

  fo = writeTag(ExpApp | (use?HasSrcPos:0)
	       ,2 + (4*sizeof(FileOffset)) + (use?sizeof(FileOffset):0));
  if (use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(fo);
  writeFileOffset(fun);
  writeByte(1);
  writeFileOffset(arg1);
  HIDE(fprintf(stderr,"\tmkResApp1 0x%x 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,fo,fun,arg1,fo);)
  return fo;
}

FileOffset
mkApp_n(FileOffset parent,FileOffset use,FileOffset fun
      ,FileOffset arg1, ... FileOffset arg_n)
{
  FileOffset fo;

  fo = writeTag(ExpApp | (use?HasSrcPos:0)
	       ,2 + (4*sizeof(FileOffset)) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset(fun);
  writeByte(_n);
  writeFileOffset(arg1);
  ...
  writeFileOffset(arg_n);
  HIDE(fprintf(stderr,"\tmkApp1 0x%x 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,Unevaluated,fun,arg1,fo);)
  return fo;
}


FileOffset
mkValueApp_n(FileOffset parent,FileOffset use,FileOffset fun
      ,FileOffset arg1, ... FileOffset arg_n)
{
  FileOffset fo;

  fo = writeTag(ExpValueApp | (use?HasSrcPos:0)
	       ,2 + (3*sizeof(FileOffset)) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(fun);
  writeByte(_n);
  writeFileOffset(arg1);
  ...
  writeFileOffset(arg_n);
  HIDE(fprintf(stderr,"\tmkValueApp1 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,fun,arg1,fo);)
  return fo;
}

FileOffset
mkChar(FileOffset parent,FileOffset use,char c)
{
  FileOffset fo;

  fo = writeTag(ExpChar | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + sizeof(char)
                + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeByte(c);
  HIDE(fprintf(stderr,"\tmkChar 0x%x 0x%x %c -> 0x%x\n",parent,use,c,fo);)
  return fo;
}

FileOffset
mkInt(FileOffset parent,FileOffset use,int i)
{
  FileOffset fo;

  fo = writeTag(ExpInt | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + sizeof(int) 
                + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeInt(i);  
  HIDE(fprintf(stderr,"\tmkInt 0x%x 0x%x %d -> 0x%x\n",parent,use,i,fo);)
  return fo;
}

FileOffset
mkInteger(FileOffset parent,FileOffset use,char *i)
{
  FileOffset fo;

  fo = writeTag(ExpInteger | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + stringSize(i) 
		+ (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeString(i);
  HIDE(fprintf(stderr,"\tmkInteger 0x%x 0x%x %s -> 0x%x\n",parent,use,i,fo);)
  return fo;
}

FileOffset
mkRat(FileOffset parent,FileOffset use,int num,int denom)
{
  FileOffset fo;

  fo = writeTag(ExpRat | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + 2*sizeof(int) 
                + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeInt(num);
  writeInt(denom);
  HIDE(fprintf(stderr,"\tmkRat 0x%x 0x%x %d/%d -> 0x%x\n",parent,use,num,denom,fo);)
  return fo;
}

FileOffset
mkRational(FileOffset parent,FileOffset use
          ,char *num,char *denom)
{
  FileOffset fo;

  fo = writeTag(ExpRational | (use?HasSrcPos:0)
	       ,1+ sizeof(FileOffset) + stringSize(num) + stringSize(denom)
                + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeString(num);
  writeString(denom);
  HIDE(fprintf(stderr,"\tmkRational 0x%x 0x%x %s/%s -> 0x%x\n",parent,use,num,denom,fo);)
  return fo;
}

FileOffset
mkFloat(FileOffset parent,FileOffset use,float f)
{
  FileOffset fo;

  fo = writeTag(ExpFloat | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + sizeof(float) 
		+ (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFloat(f);
  HIDE(fprintf(stderr,"\tmkFloat 0x%x 0x%x %f -> 0x%x\n",parent,use,f,fp);)
  return fo;
}

FileOffset
mkDouble(FileOffset parent,FileOffset use,double d)
{
  FileOffset fo;

  fo = writeTag(ExpDouble | (use?HasSrcPos:0)
	       ,1 + sizeof(FileOffset) + sizeof(double) 
		+ (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeDouble(d);
  HIDE(fprintf(stderr,"\tmkDouble 0x%x 0x%x %f -> 0x%x\n",parent,use,d,fo);)
  return fo;
}

FileOffset
mkValueUse(FileOffset parent,FileOffset use,FileOffset value)
{
  FileOffset fo;

  fo = writeTag(ExpValueUse | (use?HasSrcPos:0)
	       ,1 + 2*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(value);
  HIDE(fprintf(stderr,"\tmkValueUse 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,value,fo);)
  return fo;
}

FileOffset
mkConstUse(FileOffset parent,FileOffset use,FileOffset con)
{
  FileOffset fo;

  fo = writeTag(ExpConstUse | (use?HasSrcPos:0)
	       , 1 + 2*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(con);
  HIDE(fprintf(stderr,"\tmkConstUse 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,con,fo);)
  return fo;
}

FileOffset
mkConstDef(FileOffset context,FileOffset var)
{
  FileOffset fo;

  fo = writeTag(ExpConstDef, 1 + 3*sizeof(FileOffset));
  writeFileOffset(context);
  writeFileOffset(unevaluated);
  writeFileOffset(var);
  HIDE(fprintf(stderr,"\tmkConstDef 0x%x 0x%x -> 0x%x\n",context,var,fo);)
  return fo;
}


FileOffset
mkGuard(FileOffset parent,FileOffset use,FileOffset cond)
{
  FileOffset fo;

  fo = writeTag(ExpGuard | (use?HasSrcPos:0)
	       ,1 + 3*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset(cond);  
  HIDE(fprintf(stderr,"\tmkGuard 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,unevaluated,cond,fo);)
  return fo;
}

FileOffset
mkCase(FileOffset parent,FileOffset use,FileOffset cond)
{
  FileOffset fo;

  fo = writeTag(ExpCase | (use?HasSrcPos:0)
	       ,1 + 3*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset(cond);  
  HIDE(fprintf(stderr,"\tmkCase 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,Unevaluated,cond,fo);)
  return fo;
}

FileOffset
mkIf(FileOffset parent,FileOffset use,FileOffset cond)
{
  FileOffset fo;

  fo = writeTag(ExpIf | (use?HasSrcPos:0)
	       ,1 + 3*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset(cond);  
  HIDE(fprintf(stderr,"\tmkIf 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,Unevaluated,cond,fo);)
  return fo;
}

FileOffset
mkFieldUpdate_n(FileOffset parent,FileOffset use
              ,FileOffset arg,FileOffset binder1,FileOffset bindee1 ... FileOffset binder_n, FileOffset bindee_n)
{
  FileOffset fo;

  fo = writeTag(ExpFieldUpdate | (use?HasSrcPos:0)
	       ,2 + 5*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset(arg);
  writeByte(_n);
  writeFileOffset(binder1);
  writeFileOffset(bindee1);
  ...
  writeFileOffset(binder_n);
  writeFileOffset(bindee_n);
  HIDE(fprintf(stderr,"\tmkFieldUpdate1 0x%x 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,Unevaluated,arg,binder1,bindee1,fo);)
  return fo;
}

FileOffset
mkProjection(FileOffset parent,FileOffset use,FileOffset exp)
{
  FileOffset fo;

  fo = writeTag(ExpProjection | (use?HasSrcPos:0)
	       ,1 + 2*sizeof(FileOffset) + (use?sizeof(FileOffset):0));
  if(use)
    writeFileOffset(use);
  writeFileOffset(parent);
  writeFileOffset(exp);
  HIDE(fprintf(stderr,"\tmkProjection 0x%x 0x%x 0x%x -> 0x%x\n",parent,use,exp,fo);)
  return fo;
}

FileOffset
mkHidden(FileOffset parent)
{
  FileOffset fo = writeTag(ExpHidden,1 + 3*sizeof(FileOffset));
  writeFileOffset(parent);
  writeFileOffset(unevaluated);
  writeFileOffset((FileOffset)NULL);  /* initially empty child list */
  HIDE(fprintf(stderr,"\tmkHidden 0x%x 0x%x -> 0x%x\n",parent,Unevaluated,fo);)
  return (fo|~hiddenMask);
}

FileOffset
mkForward(FileOffset result)
{
  FileOffset fo;

  fo = writeTag(ExpForward,1 + sizeof(FileOffset));
  writeFileOffset(result);
  HIDE(fprintf(stderr,"\tmkForward 0x%x -> 0x%x\n",Unevaluated,fo);)
  return fo;
}

FileOffset
mkDoStmt(FileOffset stmt)
{
  FileOffset fo;

  fo = writeTag(ExpDoStmt, 1 + sizeof(FileOffset));
  writeFileOffset(stmt);
  HIDE(fprintf(stderr,"\tmkDoStmt 0x%x -> 0x%x\n",stmt,fo);)
  return fo;
}

/* Atom */

FileOffset
mkLambda()
{   return (htonl(Lambda)); }

FileOffset
mkDoLambda()
{   return (htonl(DoLambda)); }

FileOffset
mkVariable(FileOffset module,int begin,int end,int fixity,int arity,char *name
	  ,Bool local)
{
  FileOffset fo;

  fo = writeTag(AtomVariable | (local?LocalDef:0)
               ,1+sizeof(FileOffset)+2*sizeof(int)+2*sizeof(byte)
                +stringSize(name));
  writeFileOffset(module);
  writeInt(begin);
  writeInt(end);
  writeByte(fixity);
  writeByte(arity);
  writeString(name);
  HIDE(fprintf(stderr,"\tmkVariable 0x%x %d %d %d %d %s %d -> 0x%x\n",module,begin,end,fixity,arity,name,local,fo);)
  return fo;
}

FileOffset
mkConstructor(FileOffset module,int begin,int end,int fixity,int arity
             ,char *name)
{
  FileOffset fo;

  fo = writeTag(AtomConstructor
               ,1+sizeof(FileOffset)+2*sizeof(int)+2*sizeof(byte)
                +stringSize(name));
  writeFileOffset(module);
  writeInt(begin);
  writeInt(end);
  writeByte(fixity);
  writeByte(arity);
  writeString(name);
  HIDE(fprintf(stderr,"\tmkConstructor 0x%x %d %d %d %d %s %d -> 0x%x\n",module,begin,end,fixity,arity,name,fo);)
  return fo;
}

FileOffset
mkConstructorWFields(FileOffset module,int begin,int end,int fixity,int arity
                    ,char *name,FileOffset labels[])
{
  int i;
  FileOffset fo;

  fo = writeTag(AtomConstructor|HasFields
	       ,1+(1+arity)*sizeof(FileOffset)+2*sizeof(int)+2*sizeof(byte)
                +stringSize(name));
  writeFileOffset(module);
  writeInt(begin);
  writeInt(end);
  writeByte(fixity);
  writeByte(arity);
  writeString(name);
  for (i=0;i<arity;i++) 
    writeFileOffset(labels[i]);
  HIDE(fprintf(stderr,"\tmkConstructorWFields 0x%x %d %d %d %d %s -> 0x%x\n",module,begin,end,fixity,arity,name,fo);)
  return fo;
}


FileOffset
mkAbstract(char *description)
{
  FileOffset fo;

  fo = writeTag(AtomAbstract, 1+stringSize(description));
  writeString(description);
  HIDE(fprintf(stderr,"\tmkAbstract %s -> 0x%x\n",description,fo);)
  return fo;
}

FileOffset
mkListCons(FileOffset elem,FileOffset tail)
{
  FileOffset fo;

  fo = writeTag(ListCons,1 + 2*sizeof(FileOffset));
  writeFileOffset(elem);
  writeFileOffset(tail);
  HIDE(fprintf(stderr,"\tmkListCons 0x%x 0x%x -> 0x%x\n",elem,tail,fo);)
  return fo;
}


/* Update node that it was entered */

void entResult(FileOffset node,FileOffset use)
{
  LastExp = node;
  node &= hiddenMask;
  HIDE(fprintf(stderr,"\tentResult 0x%x 0x%x 0x%x\n",node,use,ntohl(node)+1+sizeof(FileOffset)+(use?sizeof(FileOffset):0));)
  hat_enter(ntohl(node),1+sizeof(FileOffset)+(use?sizeof(FileOffset):0),
	    entered);
  if (controlC) 
    hat_InterruptExit();
}

void entForward(FileOffset node,FileOffset hidden)
{
  hat_enter(ntohl(node),1,hidden);
  if (controlC) 
    hat_InterruptExit();
}

/* Update node with result */

void resResult(FileOffset node,FileOffset result,FileOffset use)
{
  LastExp = node;
  node &= hiddenMask;
  result &= hiddenMask;
  hat_reduce(ntohl(node),1+sizeof(FileOffset)+(use?sizeof(FileOffset):0),
	     result);
}

void resForward(FileOffset node,FileOffset result)
{
  result &= hiddenMask;
  hat_reduce(ntohl(node),1,result);
}

