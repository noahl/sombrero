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
      T.uapp1 p4v8v4v59 p4v8v4v15 p aputStrLn hputStrLn
        (T.ap1 p4v18v4v59 p (gshow p4v18v4v21 p)
          (T.cif p4v24v4v59 p (T.con0 p4v27v4v30 p True aTrue)
            (\ p ->
              T.ap1 p4v38v4v39 p (Hat.PreludeBasic.gfromInteger p4v38v4v39 p)
                  (T.conInteger p4v38v4v39 p 42)
                :: T.R Int)
            (\ p ->
              T.ap1 p4v53v4v54 p (Hat.PreludeBasic.gfromInteger p4v53v4v54 p)
                  (T.conInteger p4v53v4v54 p 24)
                :: T.R Int))))

tMain = T.mkModule "Main" "if.hs" Prelude.True

amain = T.mkVariable tMain 40001 40059 3 0 "main" Prelude.False

p4v1v4v59 = T.mkSrcPos tMain 40001 40059

p4v8v4v59 = T.mkSrcPos tMain 40008 40059

p4v8v4v15 = T.mkSrcPos tMain 40008 40015

p4v18v4v59 = T.mkSrcPos tMain 40018 40059

p4v18v4v21 = T.mkSrcPos tMain 40018 40021

p4v24v4v59 = T.mkSrcPos tMain 40024 40059

p4v27v4v30 = T.mkSrcPos tMain 40027 40030

p4v38v4v39 = T.mkSrcPos tMain 40038 40039

p4v53v4v54 = T.mkSrcPos tMain 40053 40054

main = T.traceIO "if" (Main.gmain T.mkNoSrcPos T.mkRoot)
