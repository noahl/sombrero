module Main where

and :: Int -> Int -> Int
and a b = a `seq` b `seq` if a /= (0 :: Int) then b else a

main :: IO ()
main = let x = (42 :: Int)
           y = (24 :: Int)
           z = and x y
       in z `seq` putStrLn (show z)
