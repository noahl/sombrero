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
  T.cif p4v11v4v42 p
    (T.ap2 p4v14v4v27 p (p4v16v4v17 !/= p) fa
      (T.ap1 p4v20v4v20 p (Hat.PreludeBasic.gfromInteger p4v20v4v20 p)
          (T.conInteger p4v20v4v20 p 0)
        :: T.R Int)) (\ p -> T.projection p4v35v4v35 p fb)
    (\ p -> T.projection p4v42v4v42 p fa)

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
        (T.uapp1 p10v11v10v26 p10v11v10v18 p aputStrLn hputStrLn
          (T.ap1 p10v21v10v26 p (gshow p10v21v10v24 p) (gz p10v26v10v26 p))))

tMain = T.mkModule "Main" "and.hs" Prelude.True

aand = T.mkVariable tMain 40001 40042 3 2 "and" Prelude.False

amain = T.mkVariable tMain 70001 100026 3 0 "main" Prelude.False

a7v12v7v25x = T.mkVariable tMain 70012 70025 3 0 "x" Prelude.True

a8v12v8v25y = T.mkVariable tMain 80012 80025 3 0 "y" Prelude.True

a9v12v9v22z = T.mkVariable tMain 90012 90022 3 0 "z" Prelude.True

p4v1v4v42 = T.mkSrcPos tMain 40001 40042

p4v11v4v42 = T.mkSrcPos tMain 40011 40042

p4v14v4v27 = T.mkSrcPos tMain 40014 40027

p4v16v4v17 = T.mkSrcPos tMain 40016 40017

p4v20v4v20 = T.mkSrcPos tMain 40020 40020

p4v35v4v35 = T.mkSrcPos tMain 40035 40035

p4v42v4v42 = T.mkSrcPos tMain 40042 40042

p7v1v10v26 = T.mkSrcPos tMain 70001 100026

p7v12v7v25 = T.mkSrcPos tMain 70012 70025

p7v17v7v18 = T.mkSrcPos tMain 70017 70018

p8v12v8v25 = T.mkSrcPos tMain 80012 80025

p8v17v8v18 = T.mkSrcPos tMain 80017 80018

p9v12v9v22 = T.mkSrcPos tMain 90012 90022

p9v16v9v22 = T.mkSrcPos tMain 90016 90022

p9v16v9v18 = T.mkSrcPos tMain 90016 90018

p9v20v9v20 = T.mkSrcPos tMain 90020 90020

p9v22v9v22 = T.mkSrcPos tMain 90022 90022

p10v11v10v26 = T.mkSrcPos tMain 100011 100026

p10v11v10v18 = T.mkSrcPos tMain 100011 100018

p10v21v10v26 = T.mkSrcPos tMain 100021 100026

p10v21v10v24 = T.mkSrcPos tMain 100021 100024

p10v26v10v26 = T.mkSrcPos tMain 100026 100026

main = T.traceIO "and" (Main.gmain T.mkNoSrcPos T.mkRoot)
