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
      let
        gx px p = T.constUse px p sx
        sx =
          T.constDef p a4v12v4v25x
            (\ p ->
              T.ap1 p4v17v4v18 p (Hat.PreludeBasic.gfromInteger p4v17v4v18 p)
                  (T.conInteger p4v17v4v18 p 24)
                :: T.R Int)
        gy py p = T.constUse py p sy
        sy = T.constDef p a5v12v5v16y (\ p -> gx p5v16v5v16 p) in
        (T.uapp1 p6v11v6v26 p6v11v6v18 p aputStrLn hputStrLn
          (T.ap1 p6v21v6v26 p (gshow p6v21v6v24 p) (gy p6v26v6v26 p))))

tMain = T.mkModule "Main" "two-variables.hs" Prelude.True

amain = T.mkVariable tMain 40001 60026 3 0 "main" Prelude.False

a4v12v4v25x = T.mkVariable tMain 40012 40025 3 0 "x" Prelude.True

a5v12v5v16y = T.mkVariable tMain 50012 50016 3 0 "y" Prelude.True

p4v1v6v26 = T.mkSrcPos tMain 40001 60026

p4v12v4v25 = T.mkSrcPos tMain 40012 40025

p4v17v4v18 = T.mkSrcPos tMain 40017 40018

p5v12v5v16 = T.mkSrcPos tMain 50012 50016

p5v16v5v16 = T.mkSrcPos tMain 50016 50016

p6v11v6v26 = T.mkSrcPos tMain 60011 60026

p6v11v6v18 = T.mkSrcPos tMain 60011 60018

p6v21v6v26 = T.mkSrcPos tMain 60021 60026

p6v21v6v24 = T.mkSrcPos tMain 60021 60024

p6v26v6v26 = T.mkSrcPos tMain 60026 60026

main = T.traceIO "two-variables" (Main.gmain T.mkNoSrcPos T.mkRoot)
