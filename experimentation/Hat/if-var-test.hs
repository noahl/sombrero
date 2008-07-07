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
          T.constDef p a5v7v5v22x
            (\ p -> T.con0 p5v12v5v16 p False aFalse :: T.R Bool) in
        (T.uapp1 p6v6v6v54 p6v6v6v13 p aputStrLn hputStrLn
          (T.ap1 p6v16v6v54 p (gshow p6v16v6v19 p)
            (T.cif p6v22v6v54 p (gx p6v25v6v25 p)
              (\ p ->
                T.ap1 p6v33v6v34 p (Hat.PreludeBasic.gfromInteger p6v33v6v34 p)
                    (T.conInteger p6v33v6v34 p 24)
                  :: T.R Int)
              (\ p ->
                T.ap1 p6v48v6v49 p (Hat.PreludeBasic.gfromInteger p6v48v6v49 p)
                    (T.conInteger p6v48v6v49 p 42)
                  :: T.R Int)))))

tMain = T.mkModule "Main" "if-var-test.hs" Prelude.True

amain = T.mkVariable tMain 40001 60054 3 0 "main" Prelude.False

a5v7v5v22x = T.mkVariable tMain 50007 50022 3 0 "x" Prelude.True

p4v1v6v54 = T.mkSrcPos tMain 40001 60054

p5v7v5v22 = T.mkSrcPos tMain 50007 50022

p5v12v5v16 = T.mkSrcPos tMain 50012 50016

p6v6v6v54 = T.mkSrcPos tMain 60006 60054

p6v6v6v13 = T.mkSrcPos tMain 60006 60013

p6v16v6v54 = T.mkSrcPos tMain 60016 60054

p6v16v6v19 = T.mkSrcPos tMain 60016 60019

p6v22v6v54 = T.mkSrcPos tMain 60022 60054

p6v25v6v25 = T.mkSrcPos tMain 60025 60025

p6v33v6v34 = T.mkSrcPos tMain 60033 60034

p6v48v6v49 = T.mkSrcPos tMain 60048 60049

main = T.traceIO "if-var-test" (Main.gmain T.mkNoSrcPos T.mkRoot)
