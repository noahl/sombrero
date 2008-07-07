module Main where

import qualified Hat.PreludeBasic 
import qualified Prelude 
import Prelude  hiding (map,(++),filter,concat,head,last,tail,init,null,length
  ,(!!),foldl,foldl1,scanl,scanl1,foldr,foldr1,scanr,scanr1,iterate,repeat
  ,replicate,cycle,take,drop,splitAt,takeWhile,dropWhile,span,break,lines,words
  ,unlines,unwords,reverse,and,or,any,all,elem,notElem,lookup,sum,product
  ,maximum,minimum,concatMap,zip,zip3,zipWith,zipWith3,unzip,unzip3,ReadS,ShowS
  ,Read(readsPrec,readList),Show(showsPrec,show,showList),reads,shows,read,lex
  ,showChar,showString,readParen,showParen,FilePath,IOError,ioError,userError
  ,catch,putChar,putStr,putStrLn,print,getChar,getLine,getContents,interact
  ,readFile,writeFile,appendFile,readIO,readLn,Bool(True,False),Maybe(Just
    ,Nothing),Either(Left,Right),Ordering(GT,LT,EQ),Char,String,Int,Integer
  ,Float,Double,Rational,IO,Eq((==),(/=)),Ord(compare,(<),(<=),(>),(>=),max,min)
  ,Enum(succ,pred,toEnum,fromEnum,enumFrom,enumFromThen,enumFromTo
    ,enumFromThenTo),Bounded(minBound,maxBound),Num((+),(-),(*),negate,abs
    ,signum,fromInteger),Real(toRational),Integral(quot,rem,div,mod,quotRem
    ,divMod,toInteger),Fractional((/),recip,fromRational),Floating(pi,exp,log
    ,sqrt,(**),logBase,sin,cos,tan,asin,acos,atan,sinh,cosh,tanh,asinh,acosh
    ,atanh),RealFrac(properFraction,truncate,round,ceiling,floor)
  ,RealFloat(floatRadix,floatDigits,floatRange,decodeFloat,encodeFloat,exponent
    ,significand,scaleFloat,isNaN,isInfinite,isDenormalized,isIEEE
    ,isNegativeZero,atan2),Monad((>>=),(>>),return,fail),Functor(fmap),mapM
  ,mapM_,sequence,sequence_,(=<<),maybe,either,(&&),(||),not,otherwise,subtract
  ,even,odd,gcd,lcm,(^),(^^),fromIntegral,realToFrac,fst,snd,curry,uncurry,id
  ,const,(.),flip,($),until,asTypeOf,error,undefined,seq,($!))
import Hat.Hack 
import qualified Hat.Hat as T 
import Hat.Hat  (WrapVal(wrapVal))
import Hat.Prelude 

gmain :: T.RefSrcPos -> T.RefExp -> T.R (IO T.Tuple0)

smain :: T.R (IO T.Tuple0)

gmain pmain p = T.constUse pmain p smain

smain =
  T.constDef T.mkRoot amain
    (\ p ->
      T.uapp1 p5v8v5v32 p5v8v5v15 p aputStrLn hputStrLn
        (T.ap1 p5v18v5v32 p (gshow p5v18v5v21 p)
          (T.app2 p5v24v5v32 p5v24v5v28 p apower hpower
            (T.ap1 p5v30v5v30 p (Hat.PreludeBasic.gfromInteger p5v30v5v30 p)
              (T.conInteger p5v30v5v30 p 5))
            (T.ap1 p5v32v5v32 p (Hat.PreludeBasic.gfromInteger p5v32v5v32 p)
              (T.conInteger p5v32v5v32 p 3)))))

gpower :: T.RefSrcPos -> T.RefExp -> T.R (T.Fun Integer (T.Fun Integer Integer))

hpower :: (T.R Integer) -> (T.R Integer) -> T.RefExp -> T.R Integer

gpower ppower p = T.fun2 apower ppower p hpower

hpower fb fe p =
  T.cif p9v13v9v53 p
    (T.ap2 p9v16v9v21 p (p9v18v9v19 !== p) fe
      (T.ap1 p9v21v9v21 p (Hat.PreludeBasic.gfromInteger p9v21v9v21 p)
        (T.conInteger p9v21v9v21 p 1))) (\ p -> T.projection p9v28v9v28 p fb)
    (\ p ->
      T.ap2 p9v35v9v53 p (p9v37v9v37 !* p) fb
        (T.app2 p9v40v9v53 p9v40v9v44 p apower hpower fb
          (T.ap2 p9v49v9v53 p (p9v51v9v51 !- p) fe
            (T.ap1 p9v53v9v53 p (Hat.PreludeBasic.gfromInteger p9v53v9v53 p)
              (T.conInteger p9v53v9v53 p 1)))))

tMain = T.mkModule "Main" "power.hs" Prelude.True

amain = T.mkVariable tMain 50001 50032 3 0 "main" Prelude.False

apower = T.mkVariable tMain 90001 90053 3 2 "power" Prelude.False

p5v1v5v32 = T.mkSrcPos tMain 50001 50032

p5v8v5v32 = T.mkSrcPos tMain 50008 50032

p5v8v5v15 = T.mkSrcPos tMain 50008 50015

p5v18v5v32 = T.mkSrcPos tMain 50018 50032

p5v18v5v21 = T.mkSrcPos tMain 50018 50021

p5v24v5v32 = T.mkSrcPos tMain 50024 50032

p5v24v5v28 = T.mkSrcPos tMain 50024 50028

p5v30v5v30 = T.mkSrcPos tMain 50030 50030

p5v32v5v32 = T.mkSrcPos tMain 50032 50032

p9v1v9v53 = T.mkSrcPos tMain 90001 90053

p9v13v9v53 = T.mkSrcPos tMain 90013 90053

p9v16v9v21 = T.mkSrcPos tMain 90016 90021

p9v18v9v19 = T.mkSrcPos tMain 90018 90019

p9v21v9v21 = T.mkSrcPos tMain 90021 90021

p9v28v9v28 = T.mkSrcPos tMain 90028 90028

p9v35v9v53 = T.mkSrcPos tMain 90035 90053

p9v37v9v37 = T.mkSrcPos tMain 90037 90037

p9v40v9v53 = T.mkSrcPos tMain 90040 90053

p9v40v9v44 = T.mkSrcPos tMain 90040 90044

p9v49v9v53 = T.mkSrcPos tMain 90049 90053

p9v51v9v51 = T.mkSrcPos tMain 90051 90051

p9v53v9v53 = T.mkSrcPos tMain 90053 90053

main = T.traceIO "power" (Main.gmain T.mkNoSrcPos T.mkRoot)
