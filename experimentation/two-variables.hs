module Main where

main :: IO ()
main = let x = (24 :: Int)
           y = x
       in putStrLn (show y)
