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

gand :: T.RefSrcPos -> T.RefExp -> T.R (T.Fun Int (T.Fun Int Int))

hand :: (T.R Int) -> (T.R Int) -> T.RefExp -> T.R Int

gand pand p = T.fun2 aand pand p hand

hand fa fb p =
  T.uapp2 p4v11v4v58 p4v14v4v16 p aseq hseq fa
    (T.uapp2 p4v19v4v58 p4v22v4v24 p aseq hseq fb
      (T.cif p4v27v4v58 p
        (T.ap2 p4v30v4v43 p (p4v32v4v33 !/= p) fa
          (T.ap1 p4v36v4v36 p (Hat.PreludeBasic.gfromInteger p4v36v4v36 p)
              (T.conInteger p4v36v4v36 p 0)
            :: T.R Int)) (\ p -> T.projection p4v51v4v51 p fb)
        (\ p -> T.projection p4v58v4v58 p fa)))

gmain :: T.RefSrcPos -> T.RefExp -> T.R (IO T.Tuple0)

smain :: T.R (IO T.Tuple0)

gmain pmain p = T.constUse pmain p smain

smain =
  T.constDef T.mkRoot amain
    (\ p ->
      let
        gx px p = T.constUse px p sx
        sx =
          T.constDef p a7v12v7v25x
            (\ p ->
              T.ap1 p7v17v7v18 p (Hat.PreludeBasic.gfromInteger p7v17v7v18 p)
                  (T.conInteger p7v17v7v18 p 42)
                :: T.R Int)
        gy py p = T.constUse py p sy
        sy =
          T.constDef p a8v12v8v25y
            (\ p ->
              T.ap1 p8v17v8v18 p (Hat.PreludeBasic.gfromInteger p8v17v8v18 p)
                  (T.conInteger p8v17v8v18 p 24)
                :: T.R Int)
        gz pz p = T.constUse pz p sz
        sz =
          T.constDef p a9v12v9v22z
            (\ p ->
              T.app2 p9v16v9v22 p9v16v9v18 p aand hand (gx p9v20v9v20 p)
                (gy p9v22v9v22 p)) in
        (T.uapp2 p10v11v10v34 p10v14v10v16 p aseq hseq (gz p10v11v10v11 p)
          (T.uapp1 p10v19v10v34 p10v19v10v26 p aputStrLn hputStrLn
            (T.ap1 p10v29v10v34 p (gshow p10v29v10v32 p) (gz p10v34v10v34 p)))))

tMain = T.mkModule "Main" "strict_and.hs" Prelude.True

aand = T.mkVariable tMain 40001 40058 3 2 "and" Prelude.False

amain = T.mkVariable tMain 70001 100034 3 0 "main" Prelude.False

a7v12v7v25x = T.mkVariable tMain 70012 70025 3 0 "x" Prelude.True

a8v12v8v25y = T.mkVariable tMain 80012 80025 3 0 "y" Prelude.True

a9v12v9v22z = T.mkVariable tMain 90012 90022 3 0 "z" Prelude.True

p4v1v4v58 = T.mkSrcPos tMain 40001 40058

p4v11v4v58 = T.mkSrcPos tMain 40011 40058

p4v14v4v16 = T.mkSrcPos tMain 40014 40016

p4v19v4v58 = T.mkSrcPos tMain 40019 40058

p4v22v4v24 = T.mkSrcPos tMain 40022 40024

p4v27v4v58 = T.mkSrcPos tMain 40027 40058

p4v30v4v43 = T.mkSrcPos tMain 40030 40043

p4v32v4v33 = T.mkSrcPos tMain 40032 40033

p4v36v4v36 = T.mkSrcPos tMain 40036 40036

p4v51v4v51 = T.mkSrcPos tMain 40051 40051

p4v58v4v58 = T.mkSrcPos tMain 40058 40058

p7v1v10v34 = T.mkSrcPos tMain 70001 100034

p7v12v7v25 = T.mkSrcPos tMain 70012 70025

p7v17v7v18 = T.mkSrcPos tMain 70017 70018

p8v12v8v25 = T.mkSrcPos tMain 80012 80025

p8v17v8v18 = T.mkSrcPos tMain 80017 80018

p9v12v9v22 = T.mkSrcPos tMain 90012 90022

p9v16v9v22 = T.mkSrcPos tMain 90016 90022

p9v16v9v18 = T.mkSrcPos tMain 90016 90018

p9v20v9v20 = T.mkSrcPos tMain 90020 90020

p9v22v9v22 = T.mkSrcPos tMain 90022 90022

p10v11v10v34 = T.mkSrcPos tMain 100011 100034

p10v14v10v16 = T.mkSrcPos tMain 100014 100016

p10v11v10v11 = T.mkSrcPos tMain 100011 100011

p10v19v10v34 = T.mkSrcPos tMain 100019 100034

p10v19v10v26 = T.mkSrcPos tMain 100019 100026

p10v29v10v34 = T.mkSrcPos tMain 100029 100034

p10v29v10v32 = T.mkSrcPos tMain 100029 100032

p10v34v10v34 = T.mkSrcPos tMain 100034 100034

main = T.traceIO "strict_and" (Main.gmain T.mkNoSrcPos T.mkRoot)
