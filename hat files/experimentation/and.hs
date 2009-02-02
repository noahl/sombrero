module Main where

and :: Int -> Int -> Int
and a b = if a /= (0 :: Int) then b else a

main :: IO ()
main = let x = (42 :: Int)
           y = (24 :: Int)
           z = and x y
       in putStrLn (show z)
