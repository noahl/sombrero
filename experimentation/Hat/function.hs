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
      T.uapp1 p4v8v4v40 p4v8v4v15 p aputStrLn hputStrLn
        (T.ap1 p4v18v4v40 p (gshow p4v18v4v21 p)
          (T.app1 p4v24v4v40 p4v24v4v31 p aincrease hincrease
            (T.ap1 p4v34v4v35 p (Hat.PreludeBasic.gfromInteger p4v34v4v35 p)
                (T.conInteger p4v34v4v35 p 30)
              :: T.R Int))))

gincrease :: T.RefSrcPos -> T.RefExp -> T.R (T.Fun Int Int)

hincrease :: (T.R Int) -> T.RefExp -> T.R Int

gincrease pincrease p = T.fun1 aincrease pincrease p hincrease

hincrease fx p =
  T.ap2 p7v14v7v19 p (p7v16v7v16 !+ p) fx
    (T.ap1 p7v18v7v19 p (Hat.PreludeBasic.gfromInteger p7v18v7v19 p)
      (T.conInteger p7v18v7v19 p 12))

tMain = T.mkModule "Main" "function.hs" Prelude.True

amain = T.mkVariable tMain 40001 40040 3 0 "main" Prelude.False

aincrease = T.mkVariable tMain 70001 70019 3 1 "increase" Prelude.False

p4v1v4v40 = T.mkSrcPos tMain 40001 40040

p4v8v4v40 = T.mkSrcPos tMain 40008 40040

p4v8v4v15 = T.mkSrcPos tMain 40008 40015

p4v18v4v40 = T.mkSrcPos tMain 40018 40040

p4v18v4v21 = T.mkSrcPos tMain 40018 40021

p4v24v4v40 = T.mkSrcPos tMain 40024 40040

p4v24v4v31 = T.mkSrcPos tMain 40024 40031

p4v34v4v35 = T.mkSrcPos tMain 40034 40035

p7v1v7v19 = T.mkSrcPos tMain 70001 70019

p7v14v7v19 = T.mkSrcPos tMain 70014 70019

p7v16v7v16 = T.mkSrcPos tMain 70016 70016

p7v18v7v19 = T.mkSrcPos tMain 70018 70019

main = T.traceIO "function" (Main.gmain T.mkNoSrcPos T.mkRoot)
