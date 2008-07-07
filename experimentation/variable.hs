module Main where

main :: IO ()
main = let x = (42 :: Int)
       in putStrLn (show x)
